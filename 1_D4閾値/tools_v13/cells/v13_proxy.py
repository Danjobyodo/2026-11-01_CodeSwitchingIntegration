"""(E, v9.1) Pauli-proxy engine for the torus memory experiment -- the method of studies 2 and 3
(Takada-Bartlett-Williamson, measurement-conjugated picture + Pauli dressing + Pauli proxy, run on Stim).

Purpose: an exact engine that is independent of the twisted-frame representation and, unlike the dense state vector,
runs at L = 5, 7, 9.  It is driven in lock step with the twisted-frame engine by the same protocol driver
(`protocol_shot`) as the dense reference; every dressed-measurement probability (0, 1/2, 1) and the final logical
fidelity for every decoder correction are compared.

Representation (as in study 2; ../論文草稿/研究まとめ_論文草稿_v13.md Sec. 3.3):
  physical state = E C |frame>,  C = diag((-1)^{phi0}),  E = X^x diag(omega^gamma)  (ErrorFrameTorus),
  |frame> = Pauli-stabilizer state on Stim; initially the uniform superposition over the flat configurations B0
  (stars of the three colours + the x-holonomies of `logical_colors`), so that C|frame_0> is the D4 code state of
  the main code (phi0 = 0 on the holonomy representatives, as in the dense reference).
  A dressed check G = X^s CZ^{pairs} measured on E C|frame>  ==  C^dag E^dag G E C measured on |frame>; on the flat
  subspace C^dag X^s CZ C = X^s (the D4 identity phi0(b+s) + phi0(b) = q_s(b), the same identity the twisted frame
  uses), so the measured operator is the Pauli  X^s * (Pauli dressing of E)  (ErrorFrameTorus.measured).
  Z checks: deterministic, outcome = face parity of the X frame.
  Fidelity at the end (X frame removed): F(delta) = |<frame_0| Zbar^delta diag(omega^gamma) |frame>|^2, evaluated by
  sequential post-selection of the generators of |frame_0> on a copy of the Stim state.
Circuit-level faults use the fault tables of the main code (the same composition as TFBackend); the gate-level
model of the faults is checked independently only by the dense reference at L = 3.
"""


class ErrorFrameTorus:
    """E = X^x diag(omega^gamma(a)),  gamma(a) = l.a + 4 sum_{i<j} Q_ij a_i a_j (mod 8).  Same algebra as study 2's
    ErrorFrame (chsc_switch_v9.py), restricted to the operations of the memory experiment.  Index n = dummy (0)."""

    def __init__(self, n: int):
        self.n = n
        self.x = np.zeros(n + 1, np.uint8)
        self.l = np.zeros(n + 1, np.int64)
        self.Q = np.zeros((n + 1, n + 1), np.uint8)
        self.q_dirty = False

    def reset(self):
        self.x[:] = 0
        self.l[:] = 0
        if self.q_dirty:
            self.Q[:] = 0
            self.q_dirty = False

    def left_x(self, qs):
        for q in qs:
            self.x[int(q)] ^= 1

    def left_z(self, qs):
        for q in qs:
            self.l[int(q)] = (self.l[int(q)] + 4) % 8

    def left_cz(self, pairs):
        """E <- prod CZ_ij E :  gamma(a) += 4 (a_i + x_i)(a_j + x_j)."""
        x = self.x
        for i, j in pairs:
            i, j = int(i), int(j)
            self.Q[i, j] ^= 1
            self.Q[j, i] ^= 1
            self.l[i] = (self.l[i] + 4 * int(x[j])) % 8
            self.l[j] = (self.l[j] + 4 * int(x[i])) % 8
            self.q_dirty = True

    def measured(self, S: np.ndarray, PA: np.ndarray, PB: np.ndarray, extraZ: np.ndarray):
        """E^dagger (X^S CZ^{(PA,PB)} Z^{extraZ}) E with the CZ factor replaced by its Pauli proxy (identity).
        S, extraZ: (n,) 0/1 vectors; PA, PB: CZ pairs.  Returns (L, ph): operator = omega^ph * P, P has X on S\\L,
        Y on S&L, Z on L\\S."""
        n = self.n
        x = self.x
        L = np.zeros(n + 1, np.uint8)
        c = 0
        for a, b in zip(PA, PB):                 # X frame through the CZ factors: Z dressing on the partners
            a, b = int(a), int(b)
            L[b] ^= x[a]
            L[a] ^= x[b]
            c += 4 * int(x[a] & x[b])
        L = L[:n]
        if extraZ is not None and np.any(extraZ):  # extra Z factor (CL: CZ(ancilla, data) faults): E^dag Z E = (-1)^x Z
            L ^= extraZ.astype(np.uint8)
            c += 4 * int((extraZ.astype(np.int64) & x[:n].astype(np.int64)).sum())
        l = self.l[:n]
        S64 = S.astype(np.int64)
        if np.any(l):                            # Z (sign) and S-type parts of gamma
            c -= int(S64 @ l)
            L ^= (S & ((l % 4) == 2).astype(np.uint8))
        if self.q_dirty:                         # CZ-type parts of gamma
            R = np.nonzero(self.Q[:n, :n].any(axis=1))[0]
            if R.size:
                QR = self.Q[R, :n].astype(np.int64)
                A = S64[R]
                L ^= ((A @ QR) % 2).astype(np.uint8)
                c += 4 * (int(((S64 @ QR.T) * A).sum()) // 2)
        k = int((S & L).sum())
        return L, (c - 2 * k) % 8


_PROXY_PHASE = {0: 1, 2: 1j, 4: -1, 6: -1j}


class ProxyTorusBackend:
    """Backend for `protocol_shot` (same interface as DenseBackend; never the lead in the lock-step tests)."""

    name = "pauli_proxy"

    def __init__(self, g: TFGeometry, stab: D4Stabilizers):
        if stim is None:
            raise RuntimeError("stim is required")
        self.g = g
        self.stab = stab
        n = g.n
        self.n = n
        self.E = ErrorFrameTorus(n)
        M = np.asarray(g.M_dense, np.uint8)[:n]          # (n, k)
        # generators of |frame_0>: X^{column} for every flat basis vector, Z^{z} for z in the left null space of M
        gens = [stim.PauliString.from_numpy(xs=M[:, j].astype(bool), zs=np.zeros(n, bool)) for j in range(g.k)]
        Z = _gf2_nullspace_rows(M.T.copy())                # rows z with z.M = 0
        gens += [stim.PauliString.from_numpy(xs=np.zeros(n, bool), zs=Z[i].astype(bool)) for i in range(Z.shape[0])]
        if len(gens) != n:
            raise AssertionError(f"frame_0 has {len(gens)} generators for {n} qubits")
        self.frame0_gens = gens
        tab = stim.Tableau.from_stabilizers(gens, allow_redundant=False, allow_underconstrained=False)
        sim = stim.TableauSimulator()
        sim.set_inverse_tableau(tab.inverse())
        self.sim0 = sim
        # logical Z of each holonomy coordinate: zbar_j . M = e_{hol_coords[j]}
        self.zbar = []
        for j in g.hol_coords:
            e = np.zeros(g.k, np.uint8)
            e[int(j)] = 1
            z = _gf2_solve_left(M, e)
            if z is None:
                raise AssertionError("no logical Z for a holonomy coordinate")
            self.zbar.append(np.flatnonzero(z))
        self.supp = np.asarray(g.chk_supp, np.int64)
        self.pairs = np.asarray(g.chk_pairs, np.int64)
        self.xtab = self.ztab = None
        self.stats = np.zeros(2, np.int64)                # (deterministic, random) proxy measurements
        self.reset()

    @property
    def x(self):
        return self.E.x

    def reset(self):
        self.sim = self.sim0.copy()
        self.E.reset()
        self._pend = None

    def xflip(self, q):
        self.E.left_x([q])

    def zflip(self, q):
        self.E.left_z([q])

    def cz(self, i, j):
        self.E.left_cz([(i, j)])

    def apply_stabilizer(self, ci):
        self.E.left_cz([tuple(self.pairs[ci, u]) for u in range(2)])
        self.E.left_x(self.supp[ci])

    def _op(self, ci, extraQ=()):
        n = self.n
        S = np.zeros(n, np.uint8)
        S[self.supp[ci]] = 1
        ez = np.zeros(n, np.uint8)
        for q in extraQ:
            ez[int(q)] ^= 1
        L, ph = self.E.measured(S, self.pairs[ci, :, 0], self.pairs[ci, :, 1], ez)
        if ph not in (0, 4):
            raise AssertionError("non-Hermitian Pauli-dressed operator")
        return stim.PauliString.from_numpy(xs=S.astype(bool), zs=L.astype(bool), sign=_PROXY_PHASE[int(ph)])

    def check_probs(self, ci, extraQ=()):
        ps = self._op(ci, extraQ)
        e = self.sim.peek_observable_expectation(ps)
        self._pend = (ps, e)
        if e == 0:
            return (0.5, 0.5)
        return (1.0, 0.0) if e > 0 else (0.0, 1.0)

    def check_project(self, m):
        ps, e = self._pend
        if e == 0:
            self.sim.postselect_observable(ps, desired_value=bool(m))
            self.stats[1] += 1
        else:
            self.stats[0] += 1
            if (e > 0) != (m == 0):
                raise AssertionError("projecting onto a zero-probability outcome (proxy)")

    # ---- circuit level: the fault effects are composed with the main code's fault tables (as TFBackend)
    def cl_zcheck(self, f, faults):
        X, Z, CZ, F = TFBackend._compose(self.ztab, faults)
        qs = [int(q) for q in self.g.faces[f]]
        v = int(self.E.x[qs[0]] ^ self.E.x[qs[1]] ^ self.E.x[qs[2]]) ^ F
        for u in range(3):
            if (X >> (u + 1)) & 1:
                self.xflip(qs[u])
            if (Z >> (u + 1)) & 1:
                self.zflip(qs[u])
        return v

    def cl_xcheck_probs(self, ci, faults):
        X, Z, CZ, F = TFBackend._compose(self.xtab, faults)
        g = self.g
        loc = [-1] + [int(q) for q in g.chk_supp[ci]] + [int(g.chk_pairs[ci, 0, 0]), int(g.chk_pairs[ci, 0, 1]),
                                                          int(g.chk_pairs[ci, 1, 0]), int(g.chk_pairs[ci, 1, 1])]
        Q = [loc[int(_SLOT_B[s])] for s in range(2, 6) if (CZ >> s) & 1]
        p0, p1 = self.check_probs(ci, Q)
        self._cl = (X, Z, CZ, F, loc)
        return (p0, p1) if F == 0 else (p1, p0)        # probabilities of the observed (flipped) outcome

    def cl_xcheck_project(self, o):
        X, Z, CZ, F, loc = self._cl
        self.check_project(o ^ F)
        for s in range(2):
            if (CZ >> s) & 1:
                self.cz(loc[int(_SLOT_A[s])], loc[int(_SLOT_B[s])])
        for j in range(1, 11):
            if (X >> j) & 1:
                self.xflip(loc[j])
            if (Z >> j) & 1:
                self.zflip(loc[j])

    # ---- final logical fidelity for every decoder correction delta
    def fidelities(self) -> np.ndarray:
        n = self.n
        if np.any(self.E.x[:n]):
            raise AssertionError("X frame must be removed before the fidelity is evaluated")
        circ = stim.Circuit()
        l = self.E.l[:n] % 8
        if np.any(l % 2):
            raise AssertionError("odd phase exponent (non-Clifford) in the error frame")
        for q in np.flatnonzero(l == 4):
            circ.append("Z", [int(q)])
        for q in np.flatnonzero(l == 2):
            circ.append("S", [int(q)])
        for q in np.flatnonzero(l == 6):
            circ.append("S_DAG", [int(q)])
        if self.E.q_dirty:
            ii, jj = np.nonzero(np.triu(self.E.Q[:n, :n], 1))
            for i, j in zip(ii, jj):
                circ.append("CZ", [int(i), int(j)])
        nh = len(self.zbar)
        out = np.zeros(1 << nh)
        for trial in range(1 << nh):
            sim = self.sim.copy()
            sim.do(circ)
            for hi in range(nh):
                if (trial >> hi) & 1:
                    sim.z(*[int(q) for q in self.zbar[hi]])
            prob = 1.0
            for gp in self.frame0_gens:
                e = sim.peek_observable_expectation(gp)
                if e < 0:
                    prob = 0.0
                    break
                if e == 0:
                    prob *= 0.5
                    sim.postselect_observable(gp, desired_value=False)
            out[trial] = prob
        return out


def _gf2_nullspace_rows(A: np.ndarray) -> np.ndarray:
    """Rows spanning {z : A z = 0} over GF(2) (A: (r, n))."""
    A = (np.asarray(A, np.uint8) & 1).copy()
    r, n = A.shape
    piv = []
    row = 0
    for col in range(n):
        p = None
        for i in range(row, r):
            if A[i, col]:
                p = i
                break
        if p is None:
            continue
        A[[row, p]] = A[[p, row]]
        for i in range(r):
            if i != row and A[i, col]:
                A[i] ^= A[row]
        piv.append(col)
        row += 1
        if row == r:
            break
    free = [c for c in range(n) if c not in set(piv)]
    out = np.zeros((len(free), n), np.uint8)
    for t, fc in enumerate(free):
        out[t, fc] = 1
        for i, pc in enumerate(piv):
            if A[i, fc]:
                out[t, pc] = 1
    return out


def _gf2_solve_left(M: np.ndarray, e: np.ndarray):
    """z (n,) with z.M = e (M: (n, k)), or None."""
    A = np.concatenate([np.asarray(M, np.uint8).T.copy(), np.asarray(e, np.uint8)[:, None]], axis=1)  # (k, n+1)
    k, n1 = A.shape
    n = n1 - 1
    piv = []
    row = 0
    for col in range(n):
        p = None
        for i in range(row, k):
            if A[i, col]:
                p = i
                break
        if p is None:
            continue
        A[[row, p]] = A[[p, row]]
        for i in range(k):
            if i != row and A[i, col]:
                A[i] ^= A[row]
        piv.append(col)
        row += 1
        if row == k:
            break
    if np.any(A[row:, n]):
        return None
    z = np.zeros(n, np.uint8)
    for i, pc in enumerate(piv):
        z[pc] = A[i, n]
    return z


def proxy_crosscheck(noise_model: str, L: int, p: float, shots: int, seed: int, logical_colors: str = "rgb",
                     with_dense: bool = False) -> Dict[str, float]:
    """(E) twisted frame (lead) vs Pauli proxy (and, at L=3 if with_dense, the dense state vector) in lock step:
    every dressed-measurement probability and the final fidelity for every decoder correction must agree."""
    VCFG_L = VCFG["L"]
    VCFG["L"] = int(L)
    try:
        ctx = build_validation_context(noise_model, p, logical_colors)
    finally:
        VCFG["L"] = VCFG_L
    g, stab = ctx["g"], ctx["stab"]
    tf = TFBackend(g, stab, ctx["xt"], ctx["zt"])
    px = ProxyTorusBackend(g, stab)
    px.xtab, px.ztab = ctx["xt"], ctx["zt"]
    backends = [tf, px]
    if with_dense:
        backends.append(DenseBackend(g, stab))
    rng = np.random.default_rng(seed)
    nh = len(g.hol_coords)
    max_pdev = max_fdev = 0.0
    n_ok = n_rand_tf = 0
    t0 = time.time()
    for s in range(shots):
        st0 = tf.st.stats.copy()
        r = protocol_shot(backends, g, stab, ctx["nz"], ctx["jit"], ctx["closer"], ctx["order"], rng,
                          tol=1e-6 if not with_dense else float(VCFG["lockstep_tol"]), xtab=ctx["xt"], ztab=ctx["zt"])
        max_pdev = max(max_pdev, r["maxdev"])
        n_rand_tf += int((tf.st.stats[1] - st0[1]) + (tf.st.stats[2] - st0[2]))
        if not r["flux_fail"]:
            n_ok += 1
            for trial in range(1 << nh):
                delta = [(trial >> i) & 1 for i in range(nh)]
                f_tf = logical_fidelity(r["finals"]["twisted_frame"], delta, nh)
                for b in backends[1:]:
                    max_fdev = max(max_fdev, abs(f_tf - logical_fidelity(r["finals"][b.name], delta, nh)))
    out = dict(noise_model=noise_model, L=int(L), logical_colors=logical_colors, p=p, shots=shots,
               backends="+".join(b.name for b in backends), max_prob_deviation=max_pdev,
               max_fidelity_deviation=max_fdev, shots_compared_fidelity=n_ok, random_outcomes_tf=n_rand_tf,
               proxy_random=int(px.stats[1]), proxy_deterministic=int(px.stats[0]), seconds=time.time() - t0)
    if max_pdev > (1e-6 if not with_dense else float(VCFG["lockstep_tol"])) or max_fdev > 1e-3:
        raise AssertionError(f"Pauli-proxy cross-check FAILED: {out}")
    return out


def run_proxy_crosscheck() -> pd.DataFrame:
    """(E) for VCFG["proxy_noise_models"] x VCFG["proxy_L"]; results -> <out_dir>/d4_v13_proxy_crosscheck.csv."""
    rows = []
    for nm in VCFG["proxy_noise_models"]:
        CFG["noise_model"] = nm
        for L in VCFG["proxy_L"]:
            r = proxy_crosscheck(nm, int(L), float(VCFG["proxy_p"][nm]), int(VCFG["proxy_shots"][int(L)]),
                                 int(CFG["seed"]) + 31 * int(L) + 7, str(VCFG["proxy_logical_colors"]))
            print(f"(E) Pauli proxy vs twisted frame PASSED: {r}", flush=True)
            rows.append(r)
    df = pd.DataFrame(rows)
    out_dir = str(VCFG.get("out_dir") or ".")
    os.makedirs(out_dir, exist_ok=True)
    tag = "d4_v13_proxy_crosscheck"
    if any(nm == "circuit_level" for nm in VCFG["proxy_noise_models"]):
        tag += f"_{CFG.get('circuit_noise_preset', 'legacy_v7')}"
    df.to_csv(os.path.join(out_dir, tag + ".csv"), index=False)
    return df
