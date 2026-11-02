try:
    import jax
    import jax.numpy as jnp
    from jax import lax
    JAX_AVAILABLE = True
except ImportError:  # pragma: no cover
    JAX_AVAILABLE = False


if JAX_AVAILABLE:
    def _jx_dot(a, b):
        # 注意: jnp.vdot/jnp.dot は CPU の float32 で逐次加算になり 2^24 付近で飽和する。
        # jnp.sum は木構造の縮約なので大きなベクトルでも正確。
        return jnp.sum(a * b)

    @jax.jit
    def _jx_abit(T, m, xb):
        return (lax.population_count(T & m) & 1) ^ xb

    @jax.jit
    def _jx_meas_A(psi, T, smask, m8, x8):
        Ts = T ^ smask
        a = [(lax.population_count(Ts & m8[i]) & 1) ^ x8[i] for i in range(8)]
        ph = (a[0] & a[1]) ^ (a[2] & a[3]) ^ a[4] ^ a[5] ^ a[6] ^ a[7]
        Spsi = psi[Ts] * (1 - 2 * ph).astype(psi.dtype)
        return _jx_dot(psi, Spsi), _jx_dot(psi, psi), Spsi

    @jax.jit
    def _jx_combine(psi, Spsi, sigma, scale):
        return (psi + sigma * Spsi) * scale

    @jax.jit
    def _jx_mul_z(psi, T, m, xb):
        return psi * (1 - 2 * ((lax.population_count(T & m) & 1) ^ xb)).astype(psi.dtype)

    @jax.jit
    def _jx_mul_cz(psi, T, m1, x1, m2, x2):
        a1 = (lax.population_count(T & m1) & 1) ^ x1
        a2 = (lax.population_count(T & m2) & 1) ^ x2
        return psi * (1 - 2 * (a1 & a2)).astype(psi.dtype)

    @jax.jit
    def _jx_shift(psi, T, smask):
        return psi[T ^ smask]

    @jax.jit
    def _jx_branch_combine(psi0, psi1s, sigma):
        new = (psi0 + sigma * psi1s) * np.float32(1.0 / math.sqrt(2.0))
        return new, _jx_dot(new, new)

    @jax.jit
    def _jx_scale(psi, s):
        return psi * s

    @jax.jit
    def _jx_sector_overlaps(ref, psi, T, holmask, hvals):
        prod = ref * psi
        return jnp.stack([jnp.sum(jnp.where((T & holmask) == hv, prod, 0.0)) for hv in hvals])


class DenseBackend:
    """L=3 用の密な厳密シミュレータ（JAX）。"""

    name = "dense"

    def __init__(self, g: TFGeometry, stab: D4Stabilizers, dtype=None):
        if not JAX_AVAILABLE:
            raise RuntimeError("jax is required for the dense reference")
        if g.k > 30:
            raise ValueError(f"k={g.k} is too large for the dense reference (use L=3)")
        self.g = g
        self.stab = stab
        self.dtype = jnp.float32 if dtype is None else dtype
        k = g.k
        self.N = 1 << k
        self.T = jnp.arange(self.N, dtype=jnp.int32)
        self.qmask = np.array([int(sum(int(g.M_dense[q, j]) << j for j in range(k))) for q in range(g.n)], np.int64)
        self.smask = []
        for ci in range(len(stab.vertex_X)):
            coords = g.chk_shift_coords[ci, :g.chk_shift_len[ci]]
            self.smask.append(int(sum(1 << int(j) for j in coords)))
        self.holmask = int(sum(1 << int(j) for j in g.hol_coords))
        self.hvals = []
        for h in range(1 << len(g.hol_coords)):
            v = 0
            for b, j in enumerate(g.hol_coords):
                if (h >> b) & 1:
                    v |= 1 << int(j)
            self.hvals.append(v)
        self.x = np.zeros(g.n, np.int32)
        self.psi_ref = self._initial_code_state()
        self.psi = self.psi_ref

    # --- helpers ---
    def _m(self, q):
        return np.int32(self.qmask[q])

    def _check_masks(self, ci, x, extraQ=()):
        m8 = np.zeros(8, np.int32)
        x8 = np.zeros(8, np.int32)
        pr = self.g.chk_pairs[ci]
        qs = [pr[0, 0], pr[0, 1], pr[1, 0], pr[1, 1]] + list(extraQ)
        for i, q in enumerate(qs):
            m8[i] = self.qmask[q]
            x8[i] = x[q]
        return jnp.asarray(m8), jnp.asarray(x8)

    def _initial_code_state(self):
        psi = np.zeros(self.N, np.float32)
        for hv in self.hvals:
            psi[hv] = 1.0
        psi = jnp.asarray(psi, dtype=self.dtype)
        x0 = np.zeros(self.g.n, np.int32)
        for ci in range(len(self.stab.vertex_X)):
            if int(self.g.chk_vertex[ci]) != 0:
                m8, x8 = self._check_masks(ci, x0)
                _, _, Spsi = _jx_meas_A(psi, self.T, np.int32(self.smask[ci]), m8, x8)
                psi = _jx_combine(psi, Spsi, np.float32(1.0), np.float32(0.5))
        nrm = float(jnp.sqrt(_jx_dot(psi, psi)))
        psi = _jx_scale(psi, np.float32(1.0 / nrm))
        for ci in range(len(self.stab.vertex_X)):
            m8, x8 = self._check_masks(ci, x0)
            dot, nn, _ = _jx_meas_A(psi, self.T, np.int32(self.smask[ci]), m8, x8)
            if abs(float(dot) / float(nn) - 1.0) > 1e-4:
                raise AssertionError(f"initial state not stabilized by check {ci}: {float(dot)}")
        return psi

    # --- interface used by the protocol driver ---
    def reset(self):
        self.x[:] = 0
        self.psi = self.psi_ref

    def xflip(self, q):
        self.x[q] ^= 1

    def zflip(self, q):
        self.psi = _jx_mul_z(self.psi, self.T, self._m(q), np.int32(self.x[q]))

    def cz(self, i, j):
        self.psi = _jx_mul_cz(self.psi, self.T, self._m(i), np.int32(self.x[i]), self._m(j), np.int32(self.x[j]))

    def check_probs(self, ci, extraQ=()):
        m8, x8 = self._check_masks(ci, self.x, extraQ)
        dot, nn, Spsi = _jx_meas_A(self.psi, self.T, np.int32(self.smask[ci]), m8, x8)
        e = float(dot) / float(nn)
        self._pending = (Spsi, float(nn))
        return (0.5 * (1.0 + e), 0.5 * (1.0 - e))

    def check_project(self, m):
        Spsi, nn = self._pending
        pm = 0.5 * (1.0 + (1 - 2 * m) * float(_jx_dot(self.psi, Spsi)) / nn)
        if pm < 1e-6:
            raise AssertionError("projecting onto a zero-probability outcome")
        self.psi = _jx_combine(self.psi, Spsi, np.float32(1 - 2 * m), np.float32(0.5 / math.sqrt(pm * nn)))

    def apply_stabilizer(self, ci):
        for q in self.g.chk_supp[ci]:
            self.x[q] ^= 1
        for u in range(2):
            self.cz(int(self.g.chk_pairs[ci, u, 0]), int(self.g.chk_pairs[ci, u, 1]))

    def sector_overlaps(self):
        return np.asarray(_jx_sector_overlaps(self.psi_ref, self.psi, self.T, np.int32(self.holmask),
                                              jnp.asarray(np.array(self.hvals, np.int32))), dtype=np.float64)

    # --- circuit-level (gate-level) ---
    @staticmethod
    def _by_stage(tab, faults):
        """v9: 故障の辞書 {位置番号: Pauli 番号} を {位置の名前: (種類, Pauli 番号)} に直す（故障表の stage/kind を使う）。"""
        return {tab.stage[li]: (tab.kind[li], pi) for li, pi in faults.items()}

    def cl_zcheck(self, f, faults):
        """面 Z チェック回路をゲート単位で。faults: {loc: pauli_index}（build_zcheck_fault_table の位置番号）。
        v9: 位置は故障表の名前（stage）で特定する（"uniform" と "legacy_v7" の両方の雑音の定義に対応）。"""
        fs = self._by_stage(self.ztab, faults)
        qs = [int(q) for q in self.g.faces[f]]
        amask = 0
        aconst = 0
        out_flip = 0
        # prep: legacy_v7 = R 後の D1 (X/Y -> anc 反転, Z -> 位相 (-1)^{anc} = 定数位相), uniform = X 反転（結果反転）
        def anc_pauli(pidx):
            nonlocal aconst
            px, pz = _PAULI_1Q[pidx]
            if pz:  # Z on anc: (-1)^{anc(t)}
                if amask != 0:
                    self.psi = _jx_mul_z(self.psi, self.T, np.int32(amask), np.int32(aconst))
            if px:
                aconst ^= 1
        if ("prep",) in fs:
            kind, pidx = fs[("prep",)]
            if kind == "flip":
                out_flip ^= 1
            else:
                anc_pauli(pidx)
        for i in range(3):
            q = qs[i]
            amask ^= int(self.qmask[q])
            aconst ^= int(self.x[q])
            st_ = ("cx", 1 + i)
            if st_ in fs:
                a, b = _PAULI_2Q[fs[st_][1]]  # (data, anc)
                dx, dz = _pz(a)
                if dz:
                    self.zflip(q)
                if dx:
                    self.xflip(q)
                ax, az = _pz(b)
                if az and amask != 0:
                    self.psi = _jx_mul_z(self.psi, self.T, np.int32(amask), np.int32(aconst))
                if ax:
                    aconst ^= 1
        if amask != 0 and (amask & ((1 << self.g.k) - 1)) != 0:
            # face parity mask must vanish on the flat space (sum of M rows of a face = 0)
            raise AssertionError("non-constant Z-check outcome")
        out = aconst ^ out_flip
        if ("meas",) in fs:
            out ^= 1
        return out

    def cl_xcheck_probs(self, ci, faults):
        """dressed X チェック回路（ネイティブ CCZ）をゲート単位で走らせ、結果の分布を返す。
        faults: {loc: pauli_index}（build_xcheck_fault_table の位置番号）。"""
        g = self.g
        supp = [int(q) for q in g.chk_supp[ci]]
        pairs = [(int(g.chk_pairs[ci, u, 0]), int(g.chk_pairs[ci, u, 1])) for u in range(2)]
        x0 = self.x.copy()
        x1 = self.x.copy()
        r = np.float32(1.0 / math.sqrt(2.0))
        b0 = _jx_scale(self.psi, r)
        b1 = b0
        classical = 0

        def zdata(bpsi, xf, q):
            return _jx_mul_z(bpsi, self.T, self._m(q), np.int32(xf[q]))

        def anc_pauli(pidx):
            nonlocal b0, b1, x0, x1
            px, pz = _PAULI_1Q[pidx] if pidx < 3 else (0, 0)
            if pz:
                b1 = _jx_scale(b1, np.float32(-1.0))
            if px:
                b0, b1 = b1, b0
                x0, x1 = x1, x0

        def data_pauli(q, px, pz):
            nonlocal b0, b1
            if pz:
                b0 = zdata(b0, x0, q)
                b1 = zdata(b1, x1, q)
            if px:
                x0[q] ^= 1
                x1[q] ^= 1

        fs = self._by_stage(self.xtab, faults)
        # prep: R 後の X/Y（legacy）または RX 後の Z（uniform）-> |-> (flip-type)
        if ("prep",) in fs:
            b1 = _jx_scale(b1, np.float32(-1.0))
        # h1: after H on anc (legacy_v7 only)
        if ("h1",) in fs:
            anc_pauli(fs[("h1",)][1])
        for i in range(6):
            x1[supp[i]] ^= 1  # CX(anc -> supp[i]) acts on branch 1
            st_ = ("cx", 1 + i)
            if st_ in fs:
                a, b = _PAULI_2Q[fs[st_][1]]  # (anc, data)
                ax, az = _pz(a)
                if az:
                    b1 = _jx_scale(b1, np.float32(-1.0))
                if ax:
                    b0, b1 = b1, b0
                    x0, x1 = x1, x0
                dx, dz = _pz(b)
                data_pauli(supp[i], dx, dz)
        for j, (qa, qb) in enumerate(pairs):
            b1 = _jx_mul_cz(b1, self.T, self._m(qa), np.int32(x1[qa]), self._m(qb), np.int32(x1[qb]))
            if ("ccz", j) in fs:   # v9 uniform: 3 量子ビット脱分極 D3 (anc, a, b)
                Pa, Pq1, Pq2 = _PAULI_3Q[fs[("ccz", j)][1]]
                anc_pauli({1: 0, 2: 1, 3: 2}[Pa] if Pa else 3)
                for P, qq in ((Pq1, qa), (Pq2, qb)):
                    if P:
                        px, pz = _pz(P)
                        data_pauli(qq, px, pz)
            for u, qq in enumerate((None, qa, qb)):
                st_ = ("ccz1", j, u)   # legacy_v7: 3 量子ビットそれぞれ独立に D1
                if st_ in fs:
                    if qq is None:
                        anc_pauli(fs[st_][1])
                    else:
                        px, pz = _PAULI_1Q[fs[st_][1]]
                        data_pauli(qq, px, pz)
        if ("h2",) in fs:
            classical ^= 1
        if ("meas",) in fs:
            classical ^= 1
        diff = x0 ^ x1
        sphys = np.zeros(g.n, np.int32)
        sphys[supp] = 1
        if not np.array_equal(diff, sphys):
            raise AssertionError("branch frames do not differ by the star")
        b1s = _jx_shift(b1, self.T, np.int32(self.smask[ci]))
        out = {}
        for m in (0, 1):
            new, nn = _jx_branch_combine(b0, b1s, np.float32(1 - 2 * m))
            out[m ^ classical] = (float(nn), new)
        self._pending_cl = (out, x0)
        return (out[0][0], out[1][0])

    def cl_xcheck_project(self, o):
        out, x0 = self._pending_cl
        pm, new = out[o]
        if pm < 1e-6:
            raise AssertionError("projecting onto a zero-probability outcome (CL)")
        self.psi = _jx_scale(new, np.float32(1.0 / math.sqrt(pm)))
        self.x[:] = x0


class TFBackend:
    """twisted-frame エンジンの 1 演算ずつのインターフェース（ロックステップ検証用）。"""

    name = "twisted_frame"

    def __init__(self, g: TFGeometry, stab: D4Stabilizers, xtab: Optional[FaultTable] = None,
                 ztab: Optional[FaultTable] = None):
        self.g = g
        self.stab = stab
        self.st = TFState(g)
        self.xtab = xtab
        self.ztab = ztab

    @property
    def x(self):
        return self.st.x

    def reset(self):
        self.st.reset()

    def xflip(self, q):
        self.st.x[q] ^= 1

    def zflip(self, q):
        tf_apply_z(self.g.M_packed, self.st.d, int(q))

    def cz(self, i, j):
        tf_apply_cz(self.g.M_packed, self.st.x, self.st.W, self.st.d, int(i), int(j), self.g.k)

    def _measure(self, ci, extraQ, rbit):
        Q = np.array(list(extraQ) + [0], np.int32)
        st = self.st
        g = self.g
        before = st.stats.copy()
        m = tf_measure(g.M_packed, g.chk_shift_packed, g.chk_shift_coords, g.chk_shift_len, g.chk_pairs,
                       st.x, st.W, st.d, st.G, st.rhs, st.piv, st.nrows, st.stats, int(ci), Q, len(extraQ), g.k, int(rbit))
        det = st.stats[0] > before[0]
        return int(m), (1.0 if det else 0.5)

    def check_measure(self, ci, rng):
        return self._measure(ci, (), int(rng.integers(2)))

    def apply_stabilizer(self, ci):
        tf_apply_stabilizer(self.g.M_packed, self.g.chk_supp, self.g.chk_pairs, self.st.x, self.st.W, self.st.d, int(ci), self.g.k)

    def sector_table(self):
        nh = len(self.g.hol_coords)
        a = np.zeros(1 << nh, np.uint8)
        b = np.zeros(1 << nh, np.uint8)
        tf_sector_table(self.st.W, self.st.d, self.st.G, self.st.rhs, self.st.nrows, self.g.hol_coords, self.g.k, a, b)
        return a, b

    @staticmethod
    def _compose(tab, faults):
        X = Z = CZ = F = 0
        for li in sorted(faults):
            pi = faults[li]
            nx, nz, ncz = int(tab.ex[li, pi]), int(tab.ez[li, pi]), int(tab.ecz[li, pi])
            for s in range(len(_SLOT_A)):
                if (ncz >> s) & 1:
                    a, b = int(_SLOT_A[s]), int(_SLOT_B[s])
                    if (X >> a) & 1:
                        nz ^= 1 << b
                    if (X >> b) & 1:
                        nz ^= 1 << a
            X ^= nx
            Z ^= nz
            CZ ^= ncz
            F ^= int(tab.eflip[li, pi])
        return X, Z, CZ, F

    def cl_zcheck(self, f, faults):
        X, Z, CZ, F = self._compose(self.ztab, faults)
        qs = [int(q) for q in self.g.faces[f]]
        v = int(self.st.x[qs[0]] ^ self.st.x[qs[1]] ^ self.st.x[qs[2]]) ^ F
        for u in range(3):
            if (X >> (u + 1)) & 1:
                self.xflip(qs[u])
            if (Z >> (u + 1)) & 1:
                self.zflip(qs[u])
        return v

    def cl_xcheck_measure(self, ci, faults, rng):
        X, Z, CZ, F = self._compose(self.xtab, faults)
        g = self.g
        loc = [-1] + [int(q) for q in g.chk_supp[ci]] + [int(g.chk_pairs[ci, 0, 0]), int(g.chk_pairs[ci, 0, 1]),
                                                          int(g.chk_pairs[ci, 1, 0]), int(g.chk_pairs[ci, 1, 1])]
        Q = [loc[int(_SLOT_B[s])] for s in range(2, 6) if (CZ >> s) & 1]
        m, pr = self._measure(ci, Q, int(rng.integers(2)))
        for s in range(2):
            if (CZ >> s) & 1:
                self.cz(loc[int(_SLOT_A[s])], loc[int(_SLOT_B[s])])
        for j in range(1, 11):
            if (X >> j) & 1:
                self.xflip(loc[j])
            if (Z >> j) & 1:
                self.zflip(loc[j])
        return m ^ F, pr


def _sample_faults(tab: FaultTable, rng) -> Dict[int, int]:
    out = {}
    for li in range(len(tab.prob)):
        if tab.prob[li] > 0 and rng.random() < tab.prob[li]:
            out[li] = 0 if tab.npauli[li] == 1 else int(rng.integers(tab.npauli[li]))
    return out


def protocol_shot(backends, g: TFGeometry, stab: D4Stabilizers, nz: Dict[str, object], jit: JITFluxDecoder,
                  closer: FluxCloser, order: np.ndarray, rng, tol: float = 1e-3, xtab=None, ztab=None):
    """1 ショットの記憶実験を汎用バックエンド列で実行する。
    backends[0] が結果を決め（確率に従い標本化）、残りのバックエンドはその結果の確率を計算して一致を検証し、
    同じ結果に射影する（ロックステップ）。戻り値: 検出事象列、終状態情報、確率の最大差。"""
    R = int(nz["rounds"])
    nc = len(stab.vertex_X)
    nf = g.faces.shape[0]
    for b in backends:
        b.reset()
        if b.name == "dense":   # v9: 密な計算は故障表の位置の名前で故障を特定する
            b.xtab, b.ztab = xtab, ztab
    jit.new_shot()
    xrec = np.zeros((R + 1, nc), np.uint8)
    maxdev = 0.0
    lead = backends[0]
    circuit = nz["kind"] == "circuit"

    def data_depol(p):
        for q in range(g.n):
            if rng.random() < p:
                r = int(rng.integers(3))
                for b in backends:
                    if r != 0:
                        b.zflip(q)
                    if r != 2:
                        b.xflip(q)

    def measure_dressed(ci, extra_flip, faults=None):
        nonlocal maxdev
        if faults is None:
            if lead.name == "twisted_frame":
                m, pr = lead.check_measure(ci, rng)
            else:
                p0, p1 = lead.check_probs(ci)
                m = int(rng.random() >= p0)
                pr = (p0, p1)[m]
                lead.check_project(m)
            for b in backends[1:]:
                probs = b.check_probs(ci)
                maxdev = max(maxdev, abs(probs[m] - pr))
                if abs(probs[m] - pr) > tol:
                    raise AssertionError(f"probability mismatch at check {ci}: {pr} vs {probs[m]}")
                b.check_project(m)
            return m ^ extra_flip
        if lead.name == "twisted_frame":
            o, pr = lead.cl_xcheck_measure(ci, faults, rng)
        else:
            p0, p1 = lead.cl_xcheck_probs(ci, faults)
            o = int(rng.random() >= p0)
            pr = (p0, p1)[o]
            lead.cl_xcheck_project(o)
        for b in backends[1:]:
            probs = b.cl_xcheck_probs(ci, faults)
            maxdev = max(maxdev, abs(probs[o] - pr))
            if abs(probs[o] - pr) > tol:
                raise AssertionError(f"CL probability mismatch at check {ci}: {pr} vs {probs[o]}")
            b.cl_xcheck_project(o)
        return o

    zsyn = np.zeros(nf, np.uint8)
    for t in range(R):
        if not circuit:
            data_depol(float(nz["p_data"]))
            for f in range(nf):
                v = int(lead.x[g.faces[f, 0]] ^ lead.x[g.faces[f, 1]] ^ lead.x[g.faces[f, 2]])
                zsyn[f] = v ^ int(rng.random() < float(nz["p_meas"]))
        else:
            data_depol(float(nz["params"]["idle_p"]))
            for f in range(nf):
                faults = _sample_faults(ztab, rng)
                vals = [b.cl_zcheck(f, faults) for b in backends]
                if len(set(vals)) != 1:
                    raise AssertionError("Z-check outcome mismatch")
                zsyn[f] = vals[0]
        for b in backends[1:]:
            # 同じ物理状態でも、X フレームは余境界（スタビライザの X 部分）だけ異なり得る
            # （例: CL のアンシラ X 故障は TF では S のユニタリ作用、密では分岐の入れ替えとして表される）。
            dx = (np.asarray(b.x, np.uint8)[:g.n] ^ np.asarray(lead.x, np.uint8)[:g.n])  # v7: TF 側の末尾ダミーは除く
            if coboundary_solve(g, dx) is None:
                raise AssertionError("X frames differ by more than a coboundary")
        flips = jit.step(zsyn, t)
        for q in flips:
            for b in backends:
                b.xflip(q)
            if circuit and rng.random() < float(nz["params"].get("corr_p", nz["params"]["oneq_p"])):  # v9: 補正ゲートの雑音
                r = int(rng.integers(3))
                for b in backends:
                    if r != 0:
                        b.zflip(q)
                    if r != 2:
                        b.xflip(q)
        for ci in order:
            if not circuit:
                xrec[t, ci] = measure_dressed(int(ci), int(rng.random() < float(nz["p_meas"])))
            else:
                xrec[t, ci] = measure_dressed(int(ci), 0, _sample_faults(xtab, rng))
    # terminal
    cl = closer.close(np.asarray(lead.x, np.uint8))
    for q in cl:
        for b in backends:
            b.xflip(q)
    flux_fail = coboundary_solve(g, np.asarray(lead.x, np.uint8)) is None
    if not flux_fail:
        for b in backends:  # 各バックエンドが自分のフレームを S のユニタリ作用で消す（論理状態は不変）
            mus = coboundary_solve(g, np.asarray(b.x, np.uint8))
            for c in range(3):
                for v in np.flatnonzero(mus[c]):
                    b.apply_stabilizer(int(3 * v + c))
    for ci in order:
        xrec[R, ci] = measure_dressed(int(ci), 0)
    nh = len(g.hol_coords)
    par = np.zeros(nh, np.uint8)
    for c in range(3):
        zc = np.zeros(g.E, np.uint8)
        for v in np.flatnonzero(xrec[R][c::3]):
            zc[g.root_path_edges[v]] ^= 1
        for e in np.flatnonzero(zc):
            for b in backends:
                b.zflip(int(3 * e + c))
        for hi in range(nh):
            if int(g.hol_colors[hi]) == c:
                par[hi] = int(zc[g.eta_edges].sum()) & 1
    dets = np.zeros((R + 1) * nc, np.bool_)
    prev = np.zeros(nc, np.uint8)
    for t in range(R + 1):
        dets[t * nc:(t + 1) * nc] = (xrec[t] ^ prev).astype(np.bool_)
        prev = xrec[t]
    finals = {}
    for b in backends:
        if b.name == "twisted_frame":
            finals[b.name] = ("table",) + b.sector_table()
        else:
            finals[b.name] = ("overlaps", b.sector_overlaps())
    return dict(dets=dets, par=par, flux_fail=flux_fail, finals=finals, maxdev=maxdev)


def logical_fidelity(final, delta: Sequence[int], nh: int) -> float:
    """補正後の論理忠実度 F（初期論理状態との重なりの 2 乗）。delta: 色ごとの閉じた補正鎖のカット・パリティ。"""
    hs = np.arange(1 << nh)
    sgn = np.ones(1 << nh)
    for hi in range(nh):
        if delta[hi]:
            sgn *= 1 - 2 * ((hs >> hi) & 1)
    if final[0] == "table":
        _, inn, ph = final
        amp = np.sum(np.where(inn.astype(bool), (1 - 2 * ph.astype(np.int64)) * sgn, 0))
        return float(amp * amp) / float((1 << nh) * max(1, int(inn.sum())))
    ov = final[1]
    return float(np.sum(sgn * ov)) ** 2