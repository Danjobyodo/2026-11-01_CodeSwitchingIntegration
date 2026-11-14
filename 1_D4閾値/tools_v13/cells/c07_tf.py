try:
    import numba
    from numba import njit
except ImportError:  # pragma: no cover
    numba = None
    raise RuntimeError("numba is required for the twisted-frame engine (Colab has it preinstalled).")


@dataclass
class TFGeometry:
    L: int
    n: int
    k: int
    nw: int
    V: int
    E: int
    logical_colors: str
    M_dense: np.ndarray        # (n, k) uint8: a_q = M[q] . t (+ x_q)
    M_packed: np.ndarray       # (n, nw) uint64
    chk_shift_packed: np.ndarray  # (nc, nw) uint64
    chk_shift_coords: np.ndarray  # (nc, V) int32
    chk_shift_len: np.ndarray     # (nc,) int32
    chk_supp: np.ndarray          # (nc, 6) int32  X-support qubits
    chk_pairs: np.ndarray         # (nc, 2, 2) int32 dressing CZ pairs
    chk_color: np.ndarray         # (nc,) int32
    chk_vertex: np.ndarray        # (nc,) int32
    faces: np.ndarray             # (nf, 3) int32 qubits of face-Z checks (index = 3*tri + color)
    hol_coords: np.ndarray        # (nh,) int32
    hol_colors: np.ndarray        # (nh,) int32
    eta_edges: np.ndarray         # (L*2,) edges of the vertical dual cut (= old path_x_dual)
    edge_tris: np.ndarray         # (E, 2) int32 triangles adjacent to each edge
    edge_verts: np.ndarray        # (E, 2) int32 endpoint vertex indices
    root_path_edges: List[np.ndarray]  # primal BFS tree paths from vertex 0
    tree_parent_edge: np.ndarray  # (V,) int32 parent edge in primal BFS tree (-1 root)
    tree_order: np.ndarray        # BFS order of vertices
    tree_parent_vertex: np.ndarray
    dressed: bool = True          # False なら CZ dressing を外す（= 3 枚の Z2 トーリック符号。対照実験用）
    pairs_dressed: np.ndarray = None  # 本来の dressing ペア（kappa_injection の注入先）


def _bits_to_packed(bits: np.ndarray) -> np.ndarray:
    bits = np.asarray(bits, dtype=np.uint8)
    k = bits.shape[-1]
    nw = (k + 63) // 64
    out = np.zeros(bits.shape[:-1] + (nw,), dtype=np.uint64)
    for j in range(k):
        w, b = divmod(j, 64)
        out[..., w] |= (bits[..., j].astype(np.uint64) << np.uint64(b))
    return out


def build_tf_geometry(stab: D4Stabilizers, logical_colors: str = "rgb", dressed: bool = True) -> TFGeometry:
    lat = stab.lat
    L = lat.L
    V, E = len(lat.vertices), len(lat.edges)
    n = 3 * E
    vidx = {v: i for i, v in enumerate(lat.vertices)}
    col_of = {c: i for i, c in enumerate(COLORS)}
    star_coord = {}
    k = 0
    for ci in range(3):
        for vi in range(1, V):
            star_coord[(ci, vi)] = k
            k += 1
    hol = []
    for c in logical_colors:
        hol.append((col_of[c], k))
        k += 1
    eta = []
    for y in range(L):
        eta.append(lat.edge_index_of[_canon_edge((0, y), (1, y))])
        eta.append(lat.edge_index_of[_canon_edge((0, y), (1, (y + 1) % L))])
    eta_set = set(eta)
    M = np.zeros((n, k), np.uint8)
    edge_verts = np.zeros((E, 2), np.int32)
    for e, (u, w) in enumerate(lat.edges):
        edge_verts[e] = (vidx[u], vidx[w])
        for ci, c in enumerate(COLORS):
            q = edge_color_to_qubit(e, c)
            for vv in (u, w):
                if vidx[vv] != 0:
                    M[q, star_coord[(ci, vidx[vv])]] ^= 1
            for hc, hk in hol:
                if hc == ci and e in eta_set:
                    M[q, hk] ^= 1
    nc = len(stab.vertex_X)
    shift_bits = np.zeros((nc, k), np.uint8)
    shift_coords = np.full((nc, V), -1, np.int32)
    shift_len = np.zeros(nc, np.int32)
    supp = np.zeros((nc, 6), np.int32)
    pairs = np.zeros((nc, 2, 2), np.int32)
    colr = np.zeros(nc, np.int32)
    vert = np.zeros(nc, np.int32)
    for ci_, vs in enumerate(stab.vertex_X):
        c = col_of[vs.color]
        vi = vidx[vs.vertex]
        colr[ci_] = c
        vert[ci_] = vi
        if vi != 0:
            coords = [star_coord[(c, vi)]]
        else:
            coords = [star_coord[(c, vj)] for vj in range(1, V)]
        for j in coords:
            shift_bits[ci_, j] = 1
        shift_coords[ci_, :len(coords)] = coords
        shift_len[ci_] = len(coords)
        if len(vs.x_edges) != 6 or len(vs.cz_edge_pairs) != 2:
            raise AssertionError("unexpected check shape")
        supp[ci_] = [edge_color_to_qubit(e, vs.color) for e in vs.x_edges]
        for j, (e1, e2) in enumerate(vs.cz_edge_pairs):
            pairs[ci_, j] = (edge_color_to_qubit(e1, vs.cz_colors[0]), edge_color_to_qubit(e2, vs.cz_colors[1]))
        sphys = np.zeros(n, np.uint8)
        sphys[supp[ci_]] = 1
        if not np.array_equal((M.astype(np.int64) @ shift_bits[ci_]) % 2, sphys):
            raise AssertionError("shift/star mismatch")
    faces = np.array([[edge_color_to_qubit(e, f.color) for e in f.edge_indices] for f in stab.face_Z], np.int32)
    edge_tris = np.array([lat.edge_to_triangles[e] for e in range(E)], np.int32)
    # primal BFS tree from vertex 0
    adj = [[] for _ in range(V)]
    for e in range(E):
        a, b = edge_verts[e]
        adj[a].append((b, e))
        adj[b].append((a, e))
    parent_e = np.full(V, -1, np.int32)
    parent_v = np.full(V, -1, np.int32)
    order = [0]
    seen = {0}
    head = 0
    while head < len(order):
        u = order[head]
        head += 1
        for w, e in sorted(adj[u]):
            if w not in seen:
                seen.add(w)
                parent_e[w] = e
                parent_v[w] = u
                order.append(w)
    # ダミー量子ビット（番号 n, a_n = 0 常に）を末尾に追加。dressed=False では全 CZ ペアを (n, n) にして q = 0 とする
    M_ext = np.vstack([M, np.zeros((1, k), np.uint8)])
    pairs_dressed = pairs.copy()
    if not dressed:
        pairs = np.full_like(pairs, n)
    root_paths = []
    for v in range(V):
        path = []
        u = v
        while u != 0:
            path.append(int(parent_e[u]))
            u = int(parent_v[u])
        root_paths.append(np.array(path, np.int32))
    return TFGeometry(
        L=L, n=n, k=k, nw=(k + 63) // 64, V=V, E=E, logical_colors=logical_colors,
        M_dense=M_ext, M_packed=_bits_to_packed(M_ext),
        chk_shift_packed=_bits_to_packed(shift_bits), chk_shift_coords=shift_coords, chk_shift_len=shift_len,
        chk_supp=supp, chk_pairs=pairs, chk_color=colr, chk_vertex=vert, faces=faces,
        hol_coords=np.array([hk for _, hk in hol], np.int32), hol_colors=np.array([hc for hc, _ in hol], np.int32),
        eta_edges=np.array(eta, np.int32), edge_tris=edge_tris, edge_verts=edge_verts,
        root_path_edges=root_paths, tree_parent_edge=parent_e, tree_order=np.array(order, np.int32),
        tree_parent_vertex=parent_v, dressed=bool(dressed), pairs_dressed=pairs_dressed,
    )


class TFState:
    """1 ショット分の twisted-frame 状態（numba カーネルに渡す配列の束）。"""

    def __init__(self, g: TFGeometry):
        self.g = g
        self.x = np.zeros(g.n + 1, np.uint8)  # 末尾はダミー量子ビット（常に 0）
        self.W = np.zeros((g.k, g.nw), np.uint64)
        self.d = np.zeros(g.nw, np.uint64)
        self.G = np.zeros((g.k + 1, g.nw), np.uint64)
        self.rhs = np.zeros(g.k + 1, np.uint8)
        self.piv = np.zeros(g.k + 1, np.int32)
        self.nrows = np.zeros(1, np.int32)
        self.stats = np.zeros(4, np.int64)  # [deterministic, random-case(i), random-case(ii), unused]

    def reset(self):
        self.x[:] = 0
        self.W[:] = 0
        self.d[:] = 0
        self.nrows[0] = 0


@njit
def nb_seed(seed):
    np.random.seed(seed)


@njit(inline="always")
def _popcount64(v):
    v = v - ((v >> np.uint64(1)) & np.uint64(0x5555555555555555))
    v = (v & np.uint64(0x3333333333333333)) + ((v >> np.uint64(2)) & np.uint64(0x3333333333333333))
    v = (v + (v >> np.uint64(4))) & np.uint64(0x0F0F0F0F0F0F0F0F)
    return int((v * np.uint64(0x0101010101010101)) >> np.uint64(56))


@njit(inline="always")
def _getbit(row, j):
    return int((row[j >> 6] >> np.uint64(j & 63)) & np.uint64(1))


@njit
def _dot_parity(a, b):
    s = 0
    for w in range(a.shape[0]):
        s += _popcount64(a[w] & b[w])
    return s & 1


@njit
def _is_zero(a):
    for w in range(a.shape[0]):
        if a[w] != np.uint64(0):
            return False
    return True


@njit
def _first_bit(a):
    for w in range(a.shape[0]):
        v = a[w]
        if v != np.uint64(0):
            b = 0
            while ((v >> np.uint64(b)) & np.uint64(1)) == np.uint64(0):
                b += 1
            return w * 64 + b
    return -1


@njit
def _rank2_update(W, a, b, k):
    """W += a b^T + b a^T (対角は自動的に 0 のまま)。"""
    for j in range(k):
        if _getbit(a, j):
            for w in range(W.shape[1]):
                W[j, w] ^= b[w]
        if _getbit(b, j):
            for w in range(W.shape[1]):
                W[j, w] ^= a[w]


@njit
def tf_apply_cz(Mp, x, W, d, i, j, k):
    """データ CZ(i,j): Q += (M_i t + x_i)(M_j t + x_j)。"""
    a = Mp[i]
    b = Mp[j]
    _rank2_update(W, a, b, k)
    for w in range(d.shape[0]):
        d[w] ^= a[w] & b[w]
        if x[j]:
            d[w] ^= a[w]
        if x[i]:
            d[w] ^= b[w]


@njit
def tf_apply_z(Mp, d, q):
    for w in range(d.shape[0]):
        d[w] ^= Mp[q, w]


@njit
def tf_qval(W, d, t, k):
    """Q(t) = sum_{i<j} W_ij t_i t_j + d.t  (mod 2)"""
    s = 0
    for j in range(k):
        if _getbit(t, j):
            for w in range(W.shape[1]):
                s += _popcount64(W[j, w] & t[w])
    s = s // 2
    for w in range(d.shape[0]):
        s += _popcount64(d[w] & t[w])
    return s & 1


@njit
def tf_measure(Mp, shift_p, shift_coords, shift_len, pairs, x, W, d, G, rhs, piv, nrows, stats,
               ci, extraQ, nQ, k, rbit):
    """dressed X チェック ci の理想射影測定。戻り値 = 結果ビット m (固有値 (-1)^m)。"""
    nw = W.shape[1]
    s = shift_p[ci]
    l = np.zeros(nw, np.uint64)
    # linear part: W s
    for u in range(shift_len[ci]):
        j = shift_coords[ci, u]
        for w in range(nw):
            l[w] ^= W[j, w]
    kap = tf_qval(W, d, s, k)
    for u in range(2):
        i = pairs[ci, u, 0]
        j = pairs[ci, u, 1]
        if x[j]:
            for w in range(nw):
                l[w] ^= Mp[i, w]
        if x[i]:
            for w in range(nw):
                l[w] ^= Mp[j, w]
        kap ^= (x[i] & x[j])
    for u in range(nQ):
        q = extraQ[u]
        for w in range(nw):
            l[w] ^= Mp[q, w]
        kap ^= x[q]
    nr = nrows[0]
    r0 = -1
    for r in range(nr):
        if _dot_parity(G[r], s):
            r0 = r
            break
    if r0 < 0:
        # case (i): s in dir(B)
        lr = l.copy()
        kr = kap
        for r in range(nr):
            if _getbit(lr, piv[r]):
                for w in range(nw):
                    lr[w] ^= G[r, w]
                kr ^= rhs[r]
        if _is_zero(lr):
            stats[0] += 1
            return kr
        m = rbit
        p = _first_bit(lr)
        for r in range(nr):
            if _getbit(G[r], p):
                for w in range(nw):
                    G[r, w] ^= lr[w]
                rhs[r] ^= (m ^ kr)
        for w in range(nw):
            G[nr, w] = lr[w]
        rhs[nr] = m ^ kr
        piv[nr] = p
        nrows[0] = nr + 1
        stats[1] += 1
        return m
    # case (ii): s not in dir(B)
    m = rbit
    g = G[r0].copy()
    c = rhs[r0]
    _rank2_update(W, g, l, k)
    km = (kap ^ m) & 1
    for w in range(nw):
        d[w] ^= g[w] & l[w]
        if c:
            d[w] ^= l[w]
        if km:
            d[w] ^= g[w]
    for r in range(nr):
        if r != r0 and _dot_parity(G[r], s):
            for w in range(nw):
                G[r, w] ^= g[w]
            rhs[r] ^= c
    last = nr - 1
    if r0 != last:
        for w in range(nw):
            G[r0, w] = G[last, w]
        rhs[r0] = rhs[last]
        piv[r0] = piv[last]
    nrows[0] = last
    stats[2] += 1
    return m


@njit
def tf_apply_stabilizer(Mp, supp, pairs, x, W, d, ci, k):
    """スタビライザ S_ci をユニタリとして作用（最終フラックス整理用。符号空間上は恒等）。"""
    for u in range(6):
        x[supp[ci, u]] ^= 1
    for u in range(2):
        tf_apply_cz(Mp, x, W, d, pairs[ci, u, 0], pairs[ci, u, 1], k)


@njit
def tf_sector_table(W, d, G, rhs, nrows, hol_coords, k, out_in, out_phase):
    nh = hol_coords.shape[0]
    nw = W.shape[1]
    t = np.zeros(nw, np.uint64)
    for h in range(1 << nh):
        for w in range(nw):
            t[w] = np.uint64(0)
        for b in range(nh):
            if (h >> b) & 1:
                j = hol_coords[b]
                t[j >> 6] |= np.uint64(1) << np.uint64(j & 63)
        ok = 1
        for r in range(nrows[0]):
            if _dot_parity(G[r], t) != rhs[r]:
                ok = 0
                break
        out_in[h] = ok
        out_phase[h] = tf_qval(W, d, t, k) if ok else 0


@njit
def nb_depolarize_data(Mp, x, d, n, p):
    """DEPOLARIZE1(p) を全データに: X->x 反転, Z->d 更新, Y->両方。"""
    if p <= 0.0:
        return
    for q in range(n):
        if np.random.random() < p:
            r = np.random.randint(3)
            if r != 2:
                x[q] ^= 1
            if r != 0:
                tf_apply_z(Mp, d, q)


@njit
def nb_zcheck_round(x, faces, p_flip, out):
    for f in range(faces.shape[0]):
        v = x[faces[f, 0]] ^ x[faces[f, 1]] ^ x[faces[f, 2]]
        if p_flip > 0.0 and np.random.random() < p_flip:
            v ^= 1
        out[f] = v


@njit
def nb_xcheck_round(Mp, shift_p, shift_coords, shift_len, pairs, x, W, d, G, rhs, piv, nrows, stats,
                    order, k, p_flip, out):
    dummyQ = np.zeros(1, np.int32)
    for u in range(order.shape[0]):
        ci = order[u]
        m = tf_measure(Mp, shift_p, shift_coords, shift_len, pairs, x, W, d, G, rhs, piv, nrows, stats,
                       ci, dummyQ, 0, k, np.random.randint(2))
        if p_flip > 0.0 and np.random.random() < p_flip:
            m ^= 1
        out[ci] = m