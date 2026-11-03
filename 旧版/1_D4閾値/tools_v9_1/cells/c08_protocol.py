import pymatching as _pm_mod  # noqa: F401  (import check)


# ---------------------------------------------------------------------------
# CL: gate-level fault propagation tables (native CCZ gate)
# ---------------------------------------------------------------------------

_PAULI_1Q = [(1, 0), (1, 1), (0, 1)]  # X, Y, Z  as (x, z)
_PAULI_2Q = [(a, b) for a in range(4) for b in range(4) if (a, b) != (0, 0)]  # index -> (P_first, P_second) in {0:I,1:X,2:Y,3:Z}
# v9: 3 量子ビット脱分極（ネイティブ CCZ の後、研究 3 / Takada et al. App. A2 と同じ 63 通り）。index -> (P_anc, P_a, P_b)
_PAULI_3Q = [(a, b, c) for a in range(4) for b in range(4) for c in range(4) if (a, b, c) != (0, 0, 0)]
_NPAULI_MAX = 63


def _pz(pidx):
    return {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}[pidx]


def _propagate(xm, zm, cz, gates):
    """Heisenberg 伝播 E -> U E U^dag。E = X^xm Z^zm * D（D は CZ の積で先に作用）。

    D は 2 次単項式（量子ビット対）の集合で表す。1 次の項（単一 Z）は Z^zm に吸収する（大域位相は無視）。
      CX(c->t):  パウリは通常の規則、D は z_t -> z_t + z_c の代入
      CCZ(a,b,c): X_S -> X_S * diag(CCZ(z) + CCZ(z+s))（2 次・1 次の項に展開）
      H(q):       D が q を含まない場合のみ（X<->Z）
    """
    D = set(frozenset(pr) for pr in cz)
    for gate in gates:
        kind = gate[0]
        if kind == "CX":
            c, t = gate[1], gate[2]
            if (xm >> c) & 1:
                xm ^= 1 << t
            if (zm >> t) & 1:
                zm ^= 1 << c
            newD = set()
            for mono in D:
                newD ^= {mono}
                if t in mono:
                    (u,) = tuple(mono - {t})
                    if u == c:
                        zm ^= 1 << c        # z_c z_c = z_c
                    else:
                        newD ^= {frozenset((c, u))}
            D = newD
        elif kind == "CCZ":
            qs = (gate[1], gate[2], gate[3])
            s = [(xm >> q) & 1 for q in qs]
            if any(s):
                # ANF of f(z) = z0 z1 z2 + (z0+s0)(z1+s1)(z2+s2)
                vals = []
                for zz in range(8):
                    z = [(zz >> i) & 1 for i in range(3)]
                    vals.append((z[0] & z[1] & z[2]) ^ ((z[0] ^ s[0]) & (z[1] ^ s[1]) & (z[2] ^ s[2])))
                anf = list(vals)
                for i in range(3):
                    for zz in range(8):
                        if (zz >> i) & 1:
                            anf[zz] ^= anf[zz ^ (1 << i)]
                for zz in range(1, 8):
                    if anf[zz]:
                        mono = [qs[i] for i in range(3) if (zz >> i) & 1]
                        if len(mono) == 1:
                            zm ^= 1 << mono[0]
                        elif len(mono) == 2:
                            D ^= {frozenset(mono)}
                        else:
                            raise AssertionError("cubic term cannot appear")
        elif kind == "H":
            q = gate[1]
            if any(q in mono for mono in D):
                raise AssertionError("H through CZ not supported")
            bx, bz = (xm >> q) & 1, (zm >> q) & 1
            xm = (xm & ~(1 << q)) | (bz << q)
            zm = (zm & ~(1 << q)) | (bx << q)
        else:
            raise ValueError(kind)
    return xm, zm, D


def _xcheck_circuit_gates():
    # local: 0 anc, 1..6 support, 7,8 pair0, 9,10 pair1
    g = [("H", 0)]
    g += [("CX", 0, i) for i in range(1, 7)]
    g += [("CCZ", 0, 7, 8), ("CCZ", 0, 9, 10)]
    return g


_XCHECK_CZ_SLOTS = [frozenset((7, 8)), frozenset((9, 10)),
                    frozenset((0, 7)), frozenset((0, 8)), frozenset((0, 9)), frozenset((0, 10))]


@dataclass
class FaultTable:
    prob: np.ndarray      # (nloc,)
    npauli: np.ndarray    # (nloc,) 3, 15, 63 (or 1 for a pure outcome flip)
    ex: np.ndarray        # (nloc, 63) local X mask
    ez: np.ndarray        # (nloc, 63) local Z mask
    ecz: np.ndarray       # (nloc, 63) CZ-slot mask
    eflip: np.ndarray     # (nloc, 63) outcome flip
    stage: Optional[List[tuple]] = None   # v9: 故障位置の名前（正当化コードの密な計算が位置を特定するのに使う）
    kind: Optional[List[str]] = None      # v9: "flip" / "1q" / "2q" / "3q"
    qubits: Optional[List[tuple]] = None  # v9: 局所量子ビット番号


def _local_paulis(kind: str, qs):
    if kind == "1q":
        return [((px << qs[0]), (pz << qs[0])) for px, pz in _PAULI_1Q]
    if kind == "2q":
        return [(((_pz(a)[0] << qs[0]) | (_pz(b)[0] << qs[1])), ((_pz(a)[1] << qs[0]) | (_pz(b)[1] << qs[1])))
                for a, b in _PAULI_2Q]
    if kind == "3q":
        out = []
        for trip in _PAULI_3Q:
            xm = zm = 0
            for P, q in zip(trip, qs):
                xm |= _pz(P)[0] << q
                zm |= _pz(P)[1] << q
            out.append((xm, zm))
        return out
    raise ValueError(kind)


def _fill_fault_table(locs, anc_flip_axis: str) -> FaultTable:
    """locs: (prob, local qubits, gates after, kind, stage)。anc_flip_axis: 補助量子ビットの読み出しを反転させる成分
    （"z": X 基底の読み出し = 最後の H の前の Z、"x": Z 基底の読み出し）。"""
    nloc = len(locs)
    W = _NPAULI_MAX
    tab = FaultTable(prob=np.zeros(nloc), npauli=np.zeros(nloc, np.int32), ex=np.zeros((nloc, W), np.int32),
                     ez=np.zeros((nloc, W), np.int32), ecz=np.zeros((nloc, W), np.int32),
                     eflip=np.zeros((nloc, W), np.int32), stage=[l[4] for l in locs], kind=[l[3] for l in locs],
                     qubits=[l[1] for l in locs])
    for li, (pr, qs, after, kind, _stage) in enumerate(locs):
        tab.prob[li] = _clip_prob(pr, 0.999)
        if kind == "flip":
            tab.npauli[li] = 1
            tab.eflip[li, 0] = 1
            continue
        paulis = _local_paulis(kind, qs)
        tab.npauli[li] = len(paulis)
        for pi, (xm, zm) in enumerate(paulis):
            xm2, zm2, cz = _propagate(xm, zm, set(), after)
            czmask = 0
            for pr_ in cz:
                czmask |= 1 << _XCHECK_CZ_SLOTS.index(pr_)
            tab.ex[li, pi] = xm2 & ~1
            tab.ez[li, pi] = zm2 & ~1
            tab.ecz[li, pi] = czmask
            tab.eflip[li, pi] = (zm2 & 1) if anc_flip_axis == "z" else (xm2 & 1)
    return tab


def circuit_preset(params: Dict[str, float]) -> str:
    return str(params.get("preset", "legacy_v7"))


def build_xcheck_fault_table(params: Dict[str, float], with_ccz: bool = True) -> FaultTable:
    """CL の dressed X チェック回路（ネイティブ CCZ）の故障位置と、回路末端まで伝播した効果。
    with_ccz=False は対照実験用（CCZ のない bare X チェック回路 = トーリック符号の回路）。

    v9: params["preset"] で故障位置を選ぶ。
      "uniform"  : 研究 3 と同じ（Takada et al. App. A2）。補助量子ビットの X 基底準備の後に反転 p、CX の後に D2(p)、
                   ネイティブ CCZ の後に D3(p)（63 通り）、X 基底測定の前に反転 p。H は準備・測定の一部（雑音なし）。
      "legacy_v7": v7 と同じ（R 後 D1(init_p) の X/Y 成分 = 反転、H 後 D1(oneq_p)、CX 後 D2(twoq_p)、
                   CCZ 後に 3 量子ビットそれぞれ独立に D1(noncliff_p)、最後の H 後の X/Y 成分 = 反転、読み出し反転 meas_p）"""
    gates = _xcheck_circuit_gates()
    if not with_ccz:
        gates = [gt for gt in gates if gt[0] != "CCZ"]
    uniform = circuit_preset(params) == "uniform"
    locs = []  # (prob, qubits, gates_after, kind, stage)
    if uniform:
        locs.append((params["init_p"], None, None, "flip", ("prep",)))           # RX 後の Z = 結果反転
    else:
        locs.append((2.0 / 3.0 * params["init_p"], None, None, "flip", ("prep",)))  # R 後の X/Y -> H 後に Z -> 結果反転
        locs.append((params["oneq_p"], (0,), gates[1:], "1q", ("h1",)))             # H 後
    for i in range(1, 7):
        locs.append((params["twoq_p"], (0, i), gates[i + 1:], "2q", ("cx", i)))
    for j, (a, b) in enumerate(((7, 8), (9, 10))):
        if not with_ccz:
            break
        after = gates[7 + j + 1:]
        if uniform:
            locs.append((params["noncliff_p"], (0, a, b), after, "3q", ("ccz", j)))
        else:
            for u, q in enumerate((0, a, b)):
                locs.append((params["noncliff_p"], (q,), after, "1q", ("ccz1", j, u)))
    if not uniform:
        locs.append((2.0 / 3.0 * params["oneq_p"], None, None, "flip", ("h2",)))   # 最終 H 後の X/Y
    locs.append((params["meas_p"], None, None, "flip", ("meas",)))                 # 読み出し誤り
    return _fill_fault_table(locs, "z")


def build_zcheck_fault_table(params: Dict[str, float]) -> FaultTable:
    """CL の面 Z チェック回路: anc |0>, CX(data_i -> anc) x3, Z 測定。
    v9 "uniform": 準備の後の X 反転 p（= 結果反転）、CX の後に D2(p)、測定の前に反転 p。
    "legacy_v7": 準備の後に D1(init_p)（Z 成分は CX でデータに伝わる）、CX の後に D2(twoq_p)、読み出し反転 meas_p。"""
    gates = [("CX", 1, 0), ("CX", 2, 0), ("CX", 3, 0)]
    if circuit_preset(params) == "uniform":
        locs = [(params["init_p"], None, None, "flip", ("prep",))]
    else:
        locs = [(params["init_p"], (0,), gates, "1q", ("prep",))]
    for i in range(1, 4):
        locs.append((params["twoq_p"], (i, 0), gates[i:], "2q", ("cx", i)))
    locs.append((params["meas_p"], None, None, "flip", ("meas",)))
    tab = _fill_fault_table(locs, "x")
    if np.any(tab.ecz):
        raise AssertionError("Z-check faults cannot produce CZ")
    return tab


@njit
def _sample_effect(prob, npauli, ex, ez, ecz, eflip, slot_a, slot_b):
    """故障を時間順に標本化し E_total = E_last ... E_first を合成。戻り値 (x, z, cz, flip)。"""
    X = 0
    Z = 0
    CZ = 0
    F = 0
    for li in range(prob.shape[0]):
        if prob[li] > 0.0 and np.random.random() < prob[li]:
            pi = 0 if npauli[li] == 1 else np.random.randint(npauli[li])
            nx = ex[li, pi]
            nz = ez[li, pi]
            ncz = ecz[li, pi]
            # E_new * E_acc: move P_acc through D_new
            for s in range(slot_a.shape[0]):
                if (ncz >> s) & 1:
                    a = slot_a[s]
                    b = slot_b[s]
                    if (X >> a) & 1:
                        nz ^= (1 << b)
                    if (X >> b) & 1:
                        nz ^= (1 << a)
            X ^= nx
            Z ^= nz
            CZ ^= ncz
            F ^= eflip[li, pi]
    return X, Z, CZ, F


_SLOT_A = np.array([7, 9, 0, 0, 0, 0], np.int32)
_SLOT_B = np.array([8, 10, 7, 8, 9, 10], np.int32)


@njit
def nb_cl_zcheck_round(Mp, x, d, faces, n, idle_p, prob, npauli, ex, ez, ecz, eflip, out):
    # idle noise at the start of the round
    if idle_p > 0.0:
        for q in range(n):
            if np.random.random() < idle_p:
                r = np.random.randint(3)
                if r != 2:
                    x[q] ^= 1
                if r != 0:
                    tf_apply_z(Mp, d, q)
    for f in range(faces.shape[0]):
        v = x[faces[f, 0]] ^ x[faces[f, 1]] ^ x[faces[f, 2]]
        X, Z, CZ, F = _sample_effect(prob, npauli, ex, ez, ecz, eflip, _SLOT_A, _SLOT_B)
        out[f] = v ^ F
        for u in range(3):
            q = faces[f, u]
            if (X >> (u + 1)) & 1:
                x[q] ^= 1
            if (Z >> (u + 1)) & 1:
                tf_apply_z(Mp, d, q)


@njit
def nb_cl_xcheck_round(Mp, shift_p, shift_coords, shift_len, pairs, supp, x, W, d, G, rhs, piv, nrows, stats,
                       order, k, prob, npauli, ex, ez, ecz, eflip, out):
    Q = np.zeros(4, np.int32)
    loc = np.zeros(11, np.int32)
    for u in range(order.shape[0]):
        ci = order[u]
        X, Z, CZ, F = _sample_effect(prob, npauli, ex, ez, ecz, eflip, _SLOT_A, _SLOT_B)
        loc[0] = -1
        for j in range(6):
            loc[1 + j] = supp[ci, j]
        loc[7] = pairs[ci, 0, 0]
        loc[8] = pairs[ci, 0, 1]
        loc[9] = pairs[ci, 1, 0]
        loc[10] = pairs[ci, 1, 1]
        nQ = 0
        for s in range(2, 6):
            if (CZ >> s) & 1:
                Q[nQ] = loc[_SLOT_B[s]]
                nQ += 1
        m = tf_measure(Mp, shift_p, shift_coords, shift_len, pairs, x, W, d, G, rhs, piv, nrows, stats,
                       ci, Q, nQ, k, np.random.randint(2))
        out[ci] = m ^ F
        # data D (CZ pairs) first, then data Paulis
        for s in range(2):
            if (CZ >> s) & 1:
                tf_apply_cz(Mp, x, W, d, loc[_SLOT_A[s]], loc[_SLOT_B[s]], k)
        for j in range(1, 11):
            if (X >> j) & 1:
                x[loc[j]] ^= 1
            if (Z >> j) & 1:
                tf_apply_z(Mp, d, loc[j])


@njit
def nb_apply_x_list(Mp, x, d, qs, nq, oneq_p):
    for u in range(nq):
        q = qs[u]
        x[q] ^= 1
        if oneq_p > 0.0 and np.random.random() < oneq_p:
            r = np.random.randint(3)
            if r != 2:
                x[q] ^= 1
            if r != 0:
                tf_apply_z(Mp, d, q)


# ---------------------------------------------------------------------------
# JIT flux decoder
# ---------------------------------------------------------------------------

def _llr(p, cap=30.0):
    p = float(p)
    if p <= 0.0:
        return cap
    p = min(p, 0.499)
    return float(min(cap, max(1e-3, math.log((1.0 - p) / p))))


class JITFluxDecoder:
    """色ごとの因果的（just-in-time）マッチング。

    時刻 t で、未解決のフラックス事象（補正を考慮した Z シンドロームの変化）を
    層 0..t の時空グラフ上で MWPM する。層 t の各ノードは「未来境界」に重み offset*w_t で接続。
    実事象同士が組になったものだけ、その空間射影（双対グラフ上の最短路）に X 補正を今すぐ適用し、
    境界と組になった事象は保留して次ラウンドへ持ち越す。真の誤り位置や将来の記録は使わない。
    """

    def __init__(self, g: TFGeometry, rounds: int, w_s: float, w_t: float, offset: float,
                 future_boundary: bool = True):
        """v9: future_boundary=False なら未来境界を置かない（測定誤り 0 のとき。全ての事象をその場で空間的に組にする。
        トーラスでは各色のフラックスの数は常に偶数なので、完全マッチングが必ず存在する）。"""
        self.g = g
        self.nt = 2 * g.L * g.L
        self.R = rounds
        self.future_boundary = bool(future_boundary)
        nt = self.nt
        self.matchers = []
        for t in range(rounds):
            m = pymatching.Matching()
            for layer in range(t + 1):
                base = layer * nt
                for e in range(g.E):
                    a, b = g.edge_tris[e]
                    m.add_edge(base + int(a), base + int(b), weight=w_s, merge_strategy="smallest-weight")
                if layer < t:
                    for tri in range(nt):
                        m.add_edge(base + tri, base + nt + tri, weight=w_t, merge_strategy="smallest-weight")
            if self.future_boundary:
                for tri in range(nt):
                    m.add_boundary_edge(t * nt + tri, weight=max(1e-6, offset * w_t), merge_strategy="smallest-weight")
            self.matchers.append(m)
        # dual BFS trees for spatial paths
        adj = [[] for _ in range(nt)]
        for e in range(g.E):
            a, b = g.edge_tris[e]
            adj[a].append((int(b), e))
            adj[b].append((int(a), e))
        self.par = np.full((nt, nt, 2), -1, np.int32)
        for src in range(nt):
            seen = np.zeros(nt, bool)
            seen[src] = True
            dq = [src]
            h = 0
            while h < len(dq):
                u = dq[h]
                h += 1
                for w, e in adj[u]:
                    if not seen[w]:
                        seen[w] = True
                        self.par[src, w] = (u, e)
                        dq.append(w)

    def path(self, a, b):
        out = []
        u = b
        while u != a:
            pu, e = self.par[a, u]
            out.append(int(e))
            u = int(pu)
        return out

    def new_shot(self):
        self.pending = [[] for _ in range(3)]
        self.prev = np.zeros((3, self.nt), np.uint8)
        self.corr_flux = np.zeros((3, self.nt), np.uint8)

    def step(self, zsyn: np.ndarray, t: int) -> List[int]:
        nt = self.nt
        flips: List[int] = []
        for c in range(3):
            syn = zsyn[c::3] ^ self.corr_flux[c]
            ev = np.flatnonzero(syn ^ self.prev[c])
            self.prev[c] = syn
            pend = self.pending[c]
            pend.extend((int(tri), t) for tri in ev)
            if not pend:
                continue
            det = np.zeros((t + 1) * nt, np.uint8)
            node_to_ev = {}
            for idx, (tri, te) in enumerate(pend):
                node = te * nt + tri
                det[node] ^= 1
                node_to_ev.setdefault(node, []).append(idx)
            pairs = self.matchers[t].decode_to_matched_dets_array(det)
            resolved = set()
            for a, b in pairs:
                if a < 0 or b < 0:
                    if not self.future_boundary:
                        raise AssertionError("JIT without a future boundary matched an event to the boundary")
                    continue
                ia = node_to_ev[int(a)].pop()
                ib = node_to_ev[int(b)].pop()
                resolved.add(ia)
                resolved.add(ib)
                ta, tb = pend[ia][0], pend[ib][0]
                for e in self.path(ta, tb):
                    q = 3 * e + c
                    flips.append(q)
                    t1, t2 = self.g.edge_tris[e]
                    self.corr_flux[c, t1] ^= 1
                    self.corr_flux[c, t2] ^= 1
            self.pending[c] = [ev_ for i, ev_ in enumerate(pend) if i not in resolved]
        return flips


class FluxCloser:
    """終了処理: 真の残留フラックス（完全測定）を空間 MWPM で閉じる。"""

    def __init__(self, g: TFGeometry):
        self.g = g
        nt = 2 * g.L * g.L
        self.m = pymatching.Matching()
        for e in range(g.E):
            a, b = g.edge_tris[e]
            self.m.add_edge(int(a), int(b), fault_ids={e}, weight=1.0, merge_strategy="smallest-weight")

    def close(self, x: np.ndarray) -> List[int]:
        g = self.g
        flips = []
        faces = g.faces
        flux = (x[faces[:, 0]] ^ x[faces[:, 1]] ^ x[faces[:, 2]]).astype(np.uint8)
        for c in range(3):
            syn = flux[c::3]
            if syn.any():
                corr = self.m.decode(syn)
                flips.extend(int(3 * e + c) for e in np.flatnonzero(corr))
        return flips


def coboundary_solve(g: TFGeometry, x: np.ndarray):
    """平坦な X フレーム x を色ごとに x = d(mu) と解く。解けない（非自明ホモロジー）色があれば None。"""
    mus = np.zeros((3, g.V), np.uint8)
    ok = True
    x = np.asarray(x)[:3 * g.E]  # v7: 末尾のダミー量子ビットは除く
    for c in range(3):
        xc = x[c::3]
        mu = mus[c]
        for v in g.tree_order[1:]:
            mu[v] = mu[g.tree_parent_vertex[v]] ^ xc[g.tree_parent_edge[v]]
        chk = mu[g.edge_verts[:, 0]] ^ mu[g.edge_verts[:, 1]]
        if not np.array_equal(chk, xc):
            ok = False
    return mus if ok else None


"""(Cell 8 の続き) 1 点 (L, p) の twisted-frame 記憶実験"""

_TF_CACHE: Dict[Tuple, object] = {}


def _tf_geometry_cached(L: int, logical_colors: str, dressed: bool = True):
    key = ("geom", L, logical_colors, bool(dressed))
    if key not in _TF_CACHE:
        lat = TriangulatedTorus.build(L)
        stab = build_d4_stabilizers(lat)
        _TF_CACHE[key] = (stab, build_tf_geometry(stab, logical_colors, dressed=dressed))
    return _TF_CACHE[key]


def _dressing_treatment() -> str:
    mode = str(CFG.get("dressing_treatment", "exact"))
    if mode not in ("exact", "none", "kappa_injection"):
        raise ValueError(f"unknown dressing_treatment: {mode}")
    return mode


def cl_decoder_prior_scales(params: Dict[str, float], p: float) -> Tuple[float, float]:
    """v7: CL の電荷デコーダ事前分布を、実際の回路の故障表から一次の近似で求める。
    戻り値 (data_scale, meas_scale): phenomenological 型の DEM（DEPOLARIZE1(data_scale*p) + MPP 反転 meas_scale*p）
    に入れると、データの Z 型誤り率・X チェック結果の反転率が実回路の一次の値に一致する。
      * X チェック結果の反転率 = sum_loc P(loc) * P(結果反転 | loc)
      * データ 1 量子ビットあたり 1 ラウンドの Z 型誤り率 =
          2/3*idle + (X チェック回路の各スロットに現れる回数) x (そのスロットに Z が残る確率)
          + (Z チェック回路の各スロット) x ...  + CZ 誤りは各端に確率 1/2 の Z とみなす
        （スロットごとの出現回数: X サポート 2 回、dressing ペア 4/3 回、面 2 回。三角格子トーラスの平均）"""
    xt = build_xcheck_fault_table(params)
    zt = build_zcheck_fault_table(params)

    def slot_rates(tab, nslots, trivial_mask=None):
        z = np.zeros(nslots + 1)
        flip = 0.0
        for li in range(len(tab.prob)):
            n = int(tab.npauli[li])
            for pi in range(n):
                w = float(tab.prob[li]) / n
                flip += w * int(tab.eflip[li, pi])
                if trivial_mask is not None and (int(tab.ez[li, pi]) & trivial_mask) == trivial_mask:
                    continue  # 面全体の Z は面スタビライザそのもの（状態に作用しない）
                for j in range(1, nslots + 1):
                    if (int(tab.ez[li, pi]) >> j) & 1:
                        z[j] += w
                for sidx in range(2):  # data-data CZ on a dressed pair -> Z on each end with prob 1/2
                    if (int(tab.ecz[li, pi]) >> sidx) & 1:
                        z[int(_SLOT_A[sidx])] += 0.5 * w
                        z[int(_SLOT_B[sidx])] += 0.5 * w
        return z, flip

    zx, flip_x = slot_rates(xt, 10)
    zz, _ = slot_rates(zt, 3, trivial_mask=0b1110)
    z_data = (2.0 / 3.0 * params["idle_p"] + 2.0 * float(np.mean(zx[1:7])) + (4.0 / 3.0) * float(np.mean(zx[7:11]))
              + 2.0 * float(np.mean(zz[1:4])))
    if p <= 0:
        return 1.0, 1.0
    return 1.5 * z_data / p, flip_x / p


def pair_injection_rates(noise_model: str, stab: D4Stabilizers, p: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """v7 対照実験 "kappa_injection" 用: 旧研究の r=κcp（旧サロゲートと同じ式・同じ κ）を dressing ペアごとに返す。
    戻り値 (q1, q2, r): 各ラウンド、各ペアの 2 量子ビットにそれぞれ確率 r で Z を独立に加える（IZ,ZI,ZZ = r(1-r),r(1-r),r^2）。"""
    model = _resolve_noise_model_name(noise_model)
    events = build_pairwise_dressing_events(stab)
    inc = build_dressing_qubit_incidence(events)
    q1s, q2s, rs = [], [], []
    for ev in events:
        a, b = ev.qubits
        if model == "depolarizing_surrogate_v2":
            base = float(CFG["depolarizing_dressing_scale"]) * (2.0 * float(CFG["depolarizing_data_scale"]) * p / 3.0)
            r = base * ev.multiplicity / max(1, max(inc.get(a, 1), inc.get(b, 1)))
        elif model == "phenomenological":
            r1 = float(CFG["phenomenological_kickback_scale"]) * p
            r = 1.0 - (1.0 - r1) ** ev.multiplicity  # ペアの出現ごとに独立に注入（旧版と同じ）
        else:
            r = _circuit_level_pair_kickback_rate(_resolve_circuit_level_params(p, preset="legacy_v7"), ev.multiplicity,
                                                  float(CFG["circuit_kickback_scale"]))
        q1s.append(a)
        q2s.append(b)
        rs.append(_clip_prob(r))
    return np.array(q1s, np.int32), np.array(q2s, np.int32), np.array(rs)


@njit
def nb_inject_pairs(Mp, d, q1s, q2s, rates):
    for u in range(q1s.shape[0]):
        r = rates[u]
        if r > 0.0:
            if np.random.random() < r:
                tf_apply_z(Mp, d, q1s[u])
            if np.random.random() < r:
                tf_apply_z(Mp, d, q2s[u])


def resolve_tf_noise(noise_model: str, p: float, L: int) -> Dict[str, object]:
    """ノイズモデルごとの物理パラメータ（旧 CFG のスケールをそのまま使う）。"""
    model = _resolve_noise_model_name(noise_model)
    if model == "depolarizing_surrogate_v2":
        R = int(CFG["depolarizing_rounds"]) if CFG.get("depolarizing_rounds") is not None else (
            L if CFG["rounds"] is None else int(CFG["rounds"]))
        return dict(kind="phenom", rounds=R,
                    p_data=_clip_prob(float(CFG["depolarizing_data_scale"]) * p),
                    p_meas=_clip_prob(float(CFG["depolarizing_meas_scale"]) * p))
    R = L if CFG["rounds"] is None else int(CFG["rounds"])
    if model == "phenomenological":
        return dict(kind="phenom", rounds=R,
                    p_data=_clip_prob(float(CFG["phenomenological_data_scale"]) * p),
                    p_meas=_clip_prob(float(CFG["phenomenological_meas_scale"]) * p))
    params = _resolve_circuit_level_params(p)
    return dict(kind="circuit", rounds=R, params=params)


def decoder_kappa(noise_model: str) -> float:
    """CFG["tf_decoder_kappa"]（数値、またはノイズモデル名 -> 数値 の dict）から κ_dec を取り出す。"""
    tk = CFG.get("tf_decoder_kappa", 0.0)
    if isinstance(tk, dict):
        canon = {"depolarizing_surrogate_v2": "depolarizing", "phenomenological": "phenomenological",
                 "circuit_level": "circuit_level"}[_resolve_noise_model_name(noise_model)]
        # v9.1: 回路レベルは雑音の定義ごとの値があればそれを使う（"circuit_level/uniform"）
        if canon == "circuit_level" and str(CFG.get("engine", "twisted_frame")) == "twisted_frame":
            key = f"circuit_level/{CFG.get('circuit_noise_preset', 'legacy_v7')}"
            if key in tk:
                return float(tk[key])
        return float(tk.get(canon, 0.0))
    return float(tk)


def _charge_decoder_dem(noise_model: str, stab: D4Stabilizers, rounds: int, p: float,
                        kappa: Optional[float] = None):
    """電荷側デコーダの事前分布 = 旧サロゲート回路（bare MPP + r=κcp 注入, final_noise=False）の DEM。

    κ は CFG["tf_decoder_kappa"]（v6 のデコーダ事前分布用。旧サロゲートの κ とは別の値を持てる）。
    ここでの κ は「標本化される物理」には一切入らない（物理は twisted-frame エンジンが厳密に扱う）。
    """
    model = _resolve_noise_model_name(noise_model)
    kap = decoder_kappa(noise_model) if kappa is None else float(kappa)
    floor = float(CFG.get("decoder_meas_floor_scale", 0.0))
    if model == "depolarizing_surrogate_v2":
        ms = max(float(CFG["depolarizing_meas_scale"]), floor)
        return build_depolarizing_x_circuit(stab=stab, rounds=rounds, p=p, meas_scale=ms,
                                            dressing_scale=kap, final_noise=False).dem
    if model == "phenomenological":
        ms = max(float(CFG["phenomenological_meas_scale"]), floor)
        return build_phenomenological_x_circuit(stab=stab, rounds=rounds, p=p, meas_scale=ms,
                                                kickback_scale=kap, final_noise=False).dem
    if str(CFG.get("cl_decoder_prior", "calibrated")) == "calibrated":
        # v7: 実回路の故障表から求めた Z 型データ誤り率・結果反転率を phenomenological 型の DEM に入れる
        ds, ms = cl_decoder_prior_scales(_resolve_circuit_level_params(p), p)
        return build_phenomenological_x_circuit(stab=stab, rounds=rounds, p=p, data_scale=ds, meas_scale=ms,
                                                kickback_scale=kap, final_noise=False).dem
    return build_circuit_level_x_circuit(stab=stab, rounds=rounds, p=p, final_noise=False,
                                         kickback_scale=kap).dem  # v6 と同じ（旧 CL サロゲートの集約モデル）


def cl_flux_rates_from_tables(params: Dict[str, float]) -> Tuple[float, float]:
    """v9: JIT（フラックス）復号器の重み用に、回路の故障表から一次の近似で
    (データ 1 量子ビット・1 ラウンドあたりの X 型誤り率, 面 Z チェック結果の反転率) を求める。
    スロットごとの出現回数は cl_decoder_prior_scales と同じ（X サポート 2 回、dressing ペア 4/3 回、面 2 回）。"""
    xt = build_xcheck_fault_table(params)
    zt = build_zcheck_fault_table(params)

    def xrates(tab, nslots):
        x = np.zeros(nslots + 1)
        flip = 0.0
        for li in range(len(tab.prob)):
            n = int(tab.npauli[li])
            for pi in range(n):
                w = float(tab.prob[li]) / n
                flip += w * int(tab.eflip[li, pi])
                for j in range(1, nslots + 1):
                    if (int(tab.ex[li, pi]) >> j) & 1:
                        x[j] += w
        return x, flip

    xx, _ = xrates(xt, 10)
    xz, flip_z = xrates(zt, 3)
    px = (2.0 / 3.0 * float(params["idle_p"])
          + 2.0 * float(np.mean(xx[1:7])) + (4.0 / 3.0) * float(np.mean(xx[7:11])) + 2.0 * float(np.mean(xz[1:4])))
    return px, flip_z


def _jit_weights(nz: Dict[str, object]) -> Tuple[float, float]:
    if nz["kind"] == "phenom":
        px = 2.0 / 3.0 * float(nz["p_data"])
        pm = float(nz["p_meas"])
    elif circuit_preset(nz["params"]) == "uniform":
        px, pm = cl_flux_rates_from_tables(nz["params"])   # v9: 故障表から（研究 3 の FluxDecoder と同じ考え方）
    else:
        q = nz["params"]   # legacy_v7: v7 と同じ式（v7 の本番を再現するため変更しない）
        px = (2.0 / 3.0 * q["idle_p"] + 4.0 * (8.0 / 15.0) * q["twoq_p"]
              + 3.0 * (2.0 / 3.0) * q["noncliff_p"] + 2.0 / 3.0 * q["oneq_p"])
        pm = q["meas_p"] + 2.0 / 3.0 * q["init_p"] + 3.0 * (8.0 / 15.0) * q["twoq_p"]
    return _llr(px), _llr(pm)


def _jit_future_boundary(nz: Dict[str, object]) -> bool:
    """v9: CFG["jit_future_boundary"]="auto" なら、面 Z チェックの測定誤りが 0 のとき未来境界を置かない（R1-3）。"""
    mode = str(CFG.get("jit_future_boundary", "always"))
    if mode == "always":
        return True
    if mode != "auto":
        raise ValueError(f"unknown jit_future_boundary: {mode}")
    if nz["kind"] == "phenom":
        return float(nz["p_meas"]) > 0.0
    return True


def sample_tf_memory(noise_model: str, L: int, p: float, shots: int, seed: int) -> Dict[str, np.ndarray]:
    """twisted-frame エンジンで shots 回の記憶実験を行い、検出事象などを返す（復号前）。"""
    logical_colors = str(CFG.get("logical_colors", "rgb"))
    treatment = _dressing_treatment()
    dressed = treatment == "exact"
    stab, g = _tf_geometry_cached(L, logical_colors, dressed=dressed)
    nz = resolve_tf_noise(noise_model, p, L)
    inj = pair_injection_rates(noise_model, stab, p) if treatment == "kappa_injection" else None
    R = int(nz["rounds"])
    nc = len(stab.vertex_X)
    nf = g.faces.shape[0]
    order_key = str(CFG.get("x_check_order", "rgb"))
    col_rank = {COLORS.index(c): i for i, c in enumerate(order_key)}
    order = np.array(sorted(range(nc), key=lambda ci: (col_rank[int(g.chk_color[ci])], int(g.chk_vertex[ci]))), np.int32)
    w_s, w_t = _jit_weights(nz)
    fb = _jit_future_boundary(nz)
    jkey = ("jit", L, R, round(w_s, 9), round(w_t, 9), float(CFG.get("jit_boundary_offset", 1.0)), fb)
    if jkey not in _TF_CACHE:
        _TF_CACHE[jkey] = JITFluxDecoder(g, R, w_s, w_t, float(CFG.get("jit_boundary_offset", 1.0)),
                                         future_boundary=fb)
    jit = _TF_CACHE[jkey]
    ckey = ("closer", L)
    if ckey not in _TF_CACHE:
        _TF_CACHE[ckey] = FluxCloser(g)
    closer = _TF_CACHE[ckey]
    if nz["kind"] == "circuit":
        xt = build_xcheck_fault_table(nz["params"], with_ccz=dressed)
        zt = build_zcheck_fault_table(nz["params"])
        idle_p = float(nz["params"]["idle_p"])
        corr_p = float(nz["params"].get("corr_p", nz["params"]["oneq_p"]))   # JIT の X 補正ゲートの雑音
    st = TFState(g)
    nb_seed(int(seed) % (2 ** 31 - 1))
    nh = len(g.hol_coords)
    dets = np.zeros((shots, (R + 1) * nc), np.bool_)
    sec_in = np.zeros((shots, 1 << nh), np.uint8)
    sec_ph = np.zeros((shots, 1 << nh), np.uint8)
    par = np.zeros((shots, nh), np.uint8)
    flux_fail = np.zeros(shots, np.bool_)
    zsyn = np.zeros(nf, np.uint8)
    xrec = np.zeros((R + 1, nc), np.uint8)
    n_jit_flips = 0
    # v9 診断（R1-3）: dressed X 層の直前に残っているフラックス（真の X フレームの面パリティ）と、
    # フラックスが残っていない層での測定結果の統計（stats と同じ並び: 決定的, ランダム (i), 再ランダム化 (ii), -）
    n_flux_before_x = 0          # 全ラウンドの合計（面の数）
    n_rounds_flux_before_x = 0   # フラックスが 1 つ以上残っていたラウンドの数
    stats_noflux = np.zeros(4, np.int64)
    f0, f1, f2 = g.faces[:, 0], g.faces[:, 1], g.faces[:, 2]
    for s in range(shots):
        st.reset()
        jit.new_shot()
        for t in range(R):
            if nz["kind"] == "phenom":
                nb_depolarize_data(g.M_packed, st.x, st.d, g.n, float(nz["p_data"]))
                nb_zcheck_round(st.x, g.faces, float(nz["p_meas"]), zsyn)
            else:
                nb_cl_zcheck_round(g.M_packed, st.x, st.d, g.faces, g.n, idle_p,
                                   zt.prob, zt.npauli, zt.ex, zt.ez, zt.ecz, zt.eflip, zsyn)
            flips = jit.step(zsyn, t)
            if flips:
                n_jit_flips += len(flips)
                arr = np.array(flips, np.int32)
                nb_apply_x_list(g.M_packed, st.x, st.d, arr, arr.shape[0],
                                corr_p if nz["kind"] == "circuit" else 0.0)
            if inj is not None:  # 対照実験: 旧研究の r=κcp 注入（X チェック層の直前、旧サロゲートと同じ位置）
                nb_inject_pairs(g.M_packed, st.d, inj[0], inj[1], inj[2])
            nfl = int(np.count_nonzero(st.x[f0] ^ st.x[f1] ^ st.x[f2]))
            n_flux_before_x += nfl
            if nfl:
                n_rounds_flux_before_x += 1
            else:
                st_before = st.stats.copy()
            if nz["kind"] == "phenom":
                nb_xcheck_round(g.M_packed, g.chk_shift_packed, g.chk_shift_coords, g.chk_shift_len, g.chk_pairs,
                                st.x, st.W, st.d, st.G, st.rhs, st.piv, st.nrows, st.stats,
                                order, g.k, float(nz["p_meas"]), xrec[t])
            else:
                nb_cl_xcheck_round(g.M_packed, g.chk_shift_packed, g.chk_shift_coords, g.chk_shift_len, g.chk_pairs,
                                   g.chk_supp, st.x, st.W, st.d, st.G, st.rhs, st.piv, st.nrows, st.stats,
                                   order, g.k, xt.prob, xt.npauli, xt.ex, xt.ez, xt.ecz, xt.eflip, xrec[t])
            if not nfl:
                stats_noflux += st.stats - st_before
        # ---- terminal (idealized) ----
        cl = closer.close(st.x)
        if cl:
            arr = np.array(cl, np.int32)
            nb_apply_x_list(g.M_packed, st.x, st.d, arr, arr.shape[0], 0.0)
        mus = coboundary_solve(g, st.x)
        if mus is None:
            flux_fail[s] = True
        else:
            for c in range(3):
                for v in np.flatnonzero(mus[c]):
                    tf_apply_stabilizer(g.M_packed, g.chk_supp, g.chk_pairs, st.x, st.W, st.d, int(3 * v + c), g.k)
        nb_xcheck_round(g.M_packed, g.chk_shift_packed, g.chk_shift_coords, g.chk_shift_len, g.chk_pairs,
                        st.x, st.W, st.d, st.G, st.rhs, st.piv, st.nrows, st.stats, order, g.k, 0.0, xrec[R])
        # canonical charge correction (root paths) and cut parity
        for hi in range(nh):
            par[s, hi] = 0
        for c in range(3):
            zc = np.zeros(g.E, np.uint8)
            for v in np.flatnonzero(xrec[R][c::3]):
                zc[g.root_path_edges[v]] ^= 1
            for e in np.flatnonzero(zc):
                tf_apply_z(g.M_packed, st.d, int(3 * e + c))
            for hi in range(nh):
                if int(g.hol_colors[hi]) == c:
                    par[s, hi] = int(zc[g.eta_edges].sum()) & 1
        tf_sector_table(st.W, st.d, st.G, st.rhs, st.nrows, g.hol_coords, g.k, sec_in[s], sec_ph[s])
        prev = np.zeros(nc, np.uint8)
        for t in range(R + 1):
            dets[s, t * nc:(t + 1) * nc] = (xrec[t] ^ prev).astype(np.bool_)
            prev = xrec[t]
    return dict(dets=dets, sec_in=sec_in, sec_ph=sec_ph, par=par, flux_fail=flux_fail, rounds=R,
                stats=st.stats.copy(), n_jit_flips=n_jit_flips, stab=stab, g=g, dressing_treatment=treatment,
                n_flux_before_x=n_flux_before_x, n_rounds_flux_before_x=n_rounds_flux_before_x,
                stats_noflux=stats_noflux, jit_future_boundary=fb)


def logical_failure_from_tables(sec_in: np.ndarray, sec_ph: np.ndarray, par: np.ndarray, pred: np.ndarray,
                                hol_colors: np.ndarray, rng) -> Tuple[np.ndarray, np.ndarray]:
    """セクター表と復号器予測から論理忠実度 F を計算し、確率 1-F で失敗を標本化する（ベクトル化）。

    delta_c = (復号器が予測した色 c の x 方向観測量) XOR (標準補正鎖の η カット・パリティ)
    位相 g'(h) = g_can(h) + sum_c delta_c h_c,  F = |sum_{h in supp} (-1)^{g'(h)}|^2 / (2^nh |supp|)
    """
    nh = len(hol_colors)
    shots = sec_in.shape[0]
    hs = np.arange(1 << nh)
    ph = sec_ph.astype(np.int64).copy()
    for hi in range(nh):
        delta = (pred[:, 2 * int(hol_colors[hi])].astype(np.int64) ^ par[:, hi].astype(np.int64))
        ph ^= delta[:, None] * ((hs[None, :] >> hi) & 1)
    inn = sec_in.astype(bool)
    amp = np.sum(np.where(inn, 1 - 2 * ph, 0), axis=1).astype(np.float64)
    F = amp * amp / ((1 << nh) * np.maximum(1, inn.sum(axis=1)))
    fail = rng.random(shots) < (1.0 - F)
    return fail, 1.0 - F


def decode_tf_memory(noise_model: str, L: int, p: float, samp: Dict[str, np.ndarray], seed: int,
                     matcher=None) -> Dict[str, np.ndarray]:
    stab, g = samp["stab"], samp["g"]
    R = samp["rounds"]
    if matcher is None:
        dem = _charge_decoder_dem(noise_model, stab, R, p)
        if dem.num_detectors != samp["dets"].shape[1]:
            raise AssertionError("detector layout mismatch")
        matcher = pymatching.Matching.from_detector_error_model(dem)
    # flux 側で既に失敗したショット（非自明な X ループが残った）は電荷パリティが奇数になり得るので復号しない
    ok = ~samp["flux_fail"]
    pred = np.zeros((samp["dets"].shape[0], 6), np.uint8)
    if ok.any():
        pred[ok] = np.asarray(matcher.decode_batch(samp["dets"][ok]), dtype=np.uint8)
    rng = np.random.default_rng(seed + 7919)
    fail_charge, one_minus_F = logical_failure_from_tables(samp["sec_in"], samp["sec_ph"], samp["par"], pred,
                                                           g.hol_colors, rng)
    fail_charge &= ok
    fail_flux = samp["flux_fail"]
    return dict(fail_charge=fail_charge, fail_flux=fail_flux, fail_any=fail_charge | fail_flux,
                one_minus_F=one_minus_F, flux_ok=ok)


METRIC_KEYS = ("charge", "combined", "flux")


def _metric_counts(n_charge: int, n_flux: int, n_any: int, shots: int) -> Dict[str, Tuple[int, int]]:
    """v7: 指標ごとの (失敗数, 試行数)。
    charge   = X スタビライザ側（電荷側）の失敗率。flux 側が成功したショットに条件付ける（分母 = shots - n_flux）
    combined = どちらかの失敗（v6 の logical_error_rate と同じ）
    flux     = Z スタビライザ側（終了時に非自明な X ループが残った）"""
    return {"charge": (n_charge, shots - n_flux), "combined": (n_any, shots), "flux": (n_flux, shots)}


def run_one_point_tf(*, L: int, p: float, shots: int, noise_model: str) -> Dict[str, float]:
    """twisted-frame エンジンで 1 点 (L, p) を評価する（バッチ処理）。"""
    batch = max(1, int(CFG.get("batch_size", 20000)))
    seed0 = int(np.random.SeedSequence([int(CFG.get("seed", 0)), int(L), int(round(p * 1e12)),
                                        len(str(noise_model))]).generate_state(1)[0])
    n_any = n_charge = n_flux = 0
    sum_infid_ok = 0.0
    n_frac_F = 0
    stats = np.zeros(4, np.int64)
    stats_nf = np.zeros(4, np.int64)
    n_flux_bx = n_rounds_flux_bx = 0
    jit_fb = True
    n_jit = 0
    matcher = None
    rounds = None
    ndet = nobs = 0
    done = 0
    bi = 0
    while done < shots:
        cnt = min(batch, shots - done)
        seed = (seed0 + 1000003 * bi) % (2 ** 31 - 1)
        samp = sample_tf_memory(noise_model, L, p, cnt, seed)
        if matcher is None:
            rounds = samp["rounds"]
            dem = _charge_decoder_dem(noise_model, samp["stab"], rounds, p)
            if dem.num_detectors != samp["dets"].shape[1]:
                raise AssertionError("detector layout mismatch")
            matcher = pymatching.Matching.from_detector_error_model(dem)
            ndet, nobs = dem.num_detectors, len(samp["g"].hol_coords)
        res = decode_tf_memory(noise_model, L, p, samp, seed, matcher=matcher)
        n_any += int(res["fail_any"].sum())
        n_charge += int(res["fail_charge"].sum())
        n_flux += int(res["fail_flux"].sum())
        okm = res["flux_ok"]
        sum_infid_ok += float(res["one_minus_F"][okm].sum())
        n_frac_F += int(np.sum((res["one_minus_F"][okm] > 1e-9) & (res["one_minus_F"][okm] < 1 - 1e-9)))
        stats += samp["stats"]
        stats_nf += samp["stats_noflux"]
        n_flux_bx += int(samp["n_flux_before_x"])
        n_rounds_flux_bx += int(samp["n_rounds_flux_before_x"])
        jit_fb = bool(samp["jit_future_boundary"])
        n_jit += int(samp["n_jit_flips"])
        done += cnt
        bi += 1
    alpha = 1.0 - float(CFG["confidence_level"])
    counts = _metric_counts(n_charge, n_flux, n_any, shots)
    out = {
        "engine": "twisted_frame",
        "dressing_treatment": _dressing_treatment(),
        "noise_model": str(noise_model),
        "L": float(L),
        "rounds": float(rounds),
        "p": float(p),
        "shots": float(shots),
    }
    for key in METRIC_KEYS:
        k, n = counts[key]
        ac_p, lo, hi = calc_agresti_coull_interval(max(n, 0), k, alpha)
        out[f"n_fail_{key}"] = float(k)
        out[f"n_trials_{key}"] = float(n)
        out[f"ler_{key}"] = float(k / n) if n > 0 else float("nan")
        out[f"ler_{key}_lower"] = float(lo)
        out[f"ler_{key}_upper"] = float(hi)
    prim = str(CFG.get("failure_metric", "charge"))
    if prim not in METRIC_KEYS:
        raise ValueError(f"unknown failure_metric: {prim}")
    # 旧版と同じ列名は「主指標」を指す（CSV・図・交点推定の既定）
    out.update({
        "failure_metric": prim,
        "n_failures": out[f"n_fail_{prim}"],
        "n_trials": out[f"n_trials_{prim}"],
        "logical_error_rate": out[f"ler_{prim}"],
        "ler_lower": out[f"ler_{prim}_lower"],
        "ler_upper": out[f"ler_{prim}_upper"],
        "n_detectors": float(ndet),
        "n_observables": float(nobs),
        "n_fail_charge_joint": float(n_charge),  # = charge 失敗 かつ flux 成功 の数（分母 shots で見る場合）
        "mean_infidelity_flux_ok": float(sum_infid_ok / max(1, shots - n_flux)),
        "n_fractional_F": float(n_frac_F),       # 0 < 1-F < 1 となったショット数（F が 0/1 以外になったか）
        "frac_random_outcomes": float((stats[1] + stats[2]) / max(1, stats[:3].sum())),
        "frac_rerandomized_ii": float(stats[2] / max(1, stats[:3].sum())),
        "jit_flips_per_shot": float(n_jit / shots),
        # v9 診断（R1-3）: dressed X 層の直前に残ったフラックスと、フラックスのない層でのランダムな結果
        "flux_faces_before_x_per_round": float(n_flux_bx / max(1, shots * rounds)),
        "frac_rounds_flux_before_x": float(n_rounds_flux_bx / max(1, shots * rounds)),
        "frac_random_outcomes_noflux_rounds": float((stats_nf[1] + stats_nf[2]) / max(1, stats_nf[:3].sum())),
        "frac_rerandomized_ii_noflux_rounds": float(stats_nf[2] / max(1, stats_nf[:3].sum())),
        "n_outcomes_noflux_rounds": float(stats_nf[:3].sum()),
        "jit_future_boundary": bool(jit_fb),
        "circuit_noise_preset": (str(CFG.get("circuit_noise_preset", "legacy_v7"))
                                 if _resolve_noise_model_name(noise_model) == "circuit_level" else "-"),
        "code_version": str(globals().get("CODE_VERSION", "d4_v9_1")),
        "logical_colors": str(CFG.get("logical_colors", "rgb")),
        "x_check_order": str(CFG.get("x_check_order", "rgb")),
        "jit_boundary_offset": float(CFG.get("jit_boundary_offset", 1.0)),
        "tf_decoder_kappa": decoder_kappa(noise_model),
        "cl_decoder_prior": str(CFG.get("cl_decoder_prior", "calibrated")),
        "seed": float(seed0),
    })
    return out