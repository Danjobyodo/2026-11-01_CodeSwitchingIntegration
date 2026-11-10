# ======================================================================================================
# 研究 5 のライブラリ：Clifford 階層安定化子符号（twisted Z_2^N ゲージ理論、空間 N-1 次元）と
#                      階層 N の論理ゲート R_N を実装する code switching
#
#   記号   N        : Clifford 階層の階層（N=3 が D4 符号と T ゲート、N=4 が 3 次元の符号と sqrt(T)）
#          n = N-1  : 空間次元
#          色       : 0, 1, ..., n-1（普通の色）と s = n（特別な色。switch-in で測り、switch-out で捨てる色）
#          a_c(e)   : 辺 e の色 c の量子ビットの Z 基底の値（0/1）。ゲージ場
#   位相は全て「pi / 2^Q を単位とする整数（mod 2^(Q+1)）」で厳密に扱う（浮動小数の丸めが入らない）
#
#   構成   Lattice       格子（直方体の Kuhn 三角形分割）、境界、層 Sigma_k と向き
#          terms         位相多項式（安定化子の位相、W の位相）
#          Sector        Z 型の条件（平坦＋境界条件）を満たす配位の空間。座標 z = (m, ゲージ変換のビット)
#          SampleConfig  無作為に選んだ配位の上で恒等式を確かめる（大きさの制限なし）
#          StateSim      状態ベクトルで code switching を最初から最後まで実行する（小さい格子）
#          DenseSim      辺の量子ビットを全て持つ独立な実装（ごく小さい格子。Sector の検算用）
# ======================================================================================================
import itertools
import math
import numpy as np

Q = 8                       # 位相の単位は pi / 2^Q
PI_UNIT = 1 << Q            # = pi
MOD = 1 << (Q + 1)          # = 2 pi


# ------------------------------------------------------------------------------------------------------
# 格子
# ------------------------------------------------------------------------------------------------------
class Lattice:
    """直方体 [0,L_0] x ... x [0,L_{n-1}] の Kuhn 三角形分割。

    境界    B_i = {x_i = 0}（i = 0..n-1）：色 i が 0（a_i = 0）
            B_N = {どれかの i で x_i = L_i}：a_s = 0 かつ a_0 + ... + a_{n-1} = 0
    層      Sigma_0 = 全体、Sigma_k = B_N かつ x_1 = ... = x_{k-1} = 0（k = 1..n-1）。次元 n-k
    頂点の順序は座標の辞書式順序（各単体の中で全順序になる。branching structure）。
    """

    def __init__(self, N, L):
        self.N = int(N)
        self.n = n = self.N - 1
        L = tuple(int(x) for x in L)
        if len(L) != n or min(L) < 1:
            raise ValueError('L は長さ N-1 で、各成分は 1 以上')
        self.L = L
        self.s = n                                      # 特別な色の番号
        self.verts = list(itertools.product(*[range(l + 1) for l in L]))
        self.vid = {v: i for i, v in enumerate(self.verts)}
        # 最高次元の単体と向き
        self.top = {}
        for base in itertools.product(*[range(l) for l in L]):
            for perm in itertools.permutations(range(n)):
                v = list(base)
                chain = [self.vid[tuple(v)]]
                for ax in perm:
                    v[ax] += 1
                    chain.append(self.vid[tuple(v)])
                self.top[tuple(chain)] = _perm_sign(perm)
        # 全ての単体（次元ごと）
        self.simplices = {n: sorted(self.top)}
        for k in range(n - 1, 0, -1):
            faces = set()
            for sx in self.simplices[k + 1]:
                for j in range(k + 2):
                    faces.add(sx[:j] + sx[j + 1:])
            self.simplices[k] = sorted(faces)
        self.edges = self.simplices[1]
        self.eid = {e: i for i, e in enumerate(self.edges)}
        self.E = len(self.edges)
        self.V = len(self.verts)
        self.on_BN_v = [any(x == l for x, l in zip(v, L)) for v in self.verts]
        self._build_strata()

    # --- 境界 ---
    def in_B(self, i, simplex):
        return all(self.verts[v][i] == 0 for v in simplex)

    def in_BN(self, simplex):
        return any(all(self.verts[v][i] == self.L[i] for v in simplex) for i in range(self.n))

    def in_sigma(self, k, simplex):
        if k == 0:
            return True
        return self.in_BN(simplex) and all(self.in_B(i, simplex) for i in range(1, k))

    def _build_strata(self):
        """Sigma_k の単体と、境界として誘導される向き（Stokes の定理の符号）。"""
        n = self.n
        self.sigma = [dict(self.top)]
        for k in range(1, n):
            sg = {}
            for G, sgn in self.sigma[k - 1].items():
                for j in range(len(G)):
                    F = G[:j] + G[j + 1:]
                    if self.in_sigma(k, F):
                        sg[F] = sg.get(F, 0) + (-1) ** j * sgn
            if any(abs(x) != 1 for x in sg.values()):
                raise AssertionError('誘導された向きが ±1 でない')
            self.sigma.append(sg)

    def check_orientation(self):
        """向きの検査：内部の (n-1) 単体では両側の最高次元単体からの符号が打ち消し、境界では ±1 が残る（Stokes）。"""
        acc = {}
        for G, sgn in self.top.items():
            for j in range(len(G)):
                F = G[:j] + G[j + 1:]
                acc.setdefault(F, []).append((-1) ** j * sgn)
        for F, v in acc.items():
            on_bdry = self.in_BN(F) or any(self.in_B(i, F) for i in range(self.n))
            if (on_bdry and len(v) != 1) or (not on_bdry and (len(v) != 2 or sum(v) != 0)):
                return False
        return True

    # --- 頂点ごとのゲージ群 ---
    def alive_colors(self, v):
        """頂点 v でゲージ変換できる普通の色（v を含む境界 B_i が殺していない色）。"""
        return [i for i in range(self.n) if self.verts[v][i] != 0]

    def gauge_generators(self):
        """許されるゲージ変換の生成元 (v, 色の組)。B_N の外：各色を単独で。B_N の上：色の対 (j0, j)。"""
        gens = []
        for v in range(self.V):
            J = self.alive_colors(v)
            if not self.on_BN_v[v]:
                gens += [(v, (j,)) for j in J] + [(v, (self.s,))]
            else:
                gens += [(v, (J[0], j)) for j in J[1:]]
        return gens

    def qubit_counts(self):
        """物理量子ビットの数（境界条件で |0> に固定される量子ビットを除く）。"""
        n, s = self.n, self.s
        data = 0
        for e in self.edges:
            for c in range(n):
                if not self.in_B(c, e):
                    data += 1
            if not self.in_BN(e):
                data += 1
        pauli = sum(1 for e in self.edges for c in range(n) if not self.in_B(c, e))
        return dict(total=data, pauli_code=pauli, special=data - pauli, edges=self.E, vertices=self.V,
                    top_simplices=len(self.top))


def _perm_sign(perm):
    sgn, p = 1, list(perm)
    for i in range(len(p)):
        while p[i] != i:
            j = p[i]
            p[i], p[j] = p[j], p[i]
            sgn = -sgn
    return sgn


# ------------------------------------------------------------------------------------------------------
# 位相多項式。項 = (係数, 因子の列, 符号ビットの列)。値 = 係数 * prod a(因子) * (-1)^(sum a(符号ビット))
# ------------------------------------------------------------------------------------------------------
def stabilizer_terms(lat, c, v):
    """X 型安定化子 S^c_v = (v のまわりの色 c の X の積) x exp(i pi f)。f の項を返す。

    ねじれは a_0 u a_s u a_1 u ... u a_{n-1}（色の並び C = [0, s, 1, ..., n-1]）。
    f = int (C の中の色 c の位置を 0-コチェイン v に置き換えたカップ積)。
    """
    C = [0, lat.s] + list(range(1, lat.n))
    p = C.index(c)
    terms = {}
    for sx in lat.top:
        if sx[p] != v:
            continue
        fac = []
        for q in range(lat.N):
            if q < p:
                fac.append((C[q], lat.eid[(sx[q], sx[q + 1])]))
            elif q > p:
                fac.append((C[q], lat.eid[(sx[q - 1], sx[q])]))
        key = tuple(sorted(fac))
        terms[key] = terms.get(key, 0) ^ 1
    return [(PI_UNIT, list(k), []) for k, par in terms.items() if par]


def alpha_term(lat, simplex, colors, coef, dressing=True):
    """alpha_m(b_1..b_{m-1}) = (1/2) prod_i b_i(e_i) (-1)^{sum_{2<=k<j} b_j(e_k)} の、1 つの単体での項。"""
    m = len(colors)
    eids = [lat.eid[(simplex[i], simplex[i + 1])] for i in range(m)]
    fac = [(colors[i], eids[i]) for i in range(m)]
    sgn = [(colors[j], eids[k]) for k in range(1, m) for j in range(k + 1, m)] if dressing else []
    return (coef, fac, sgn)


def W_terms(lat, max_k=None, dressing=True, alternate=True, drop=()):
    """W = exp(i pi f)、f = sum_k (-1/2)^k int_{Sigma_k} alpha_{N-k}(a_0, a_{k+1}, ..., a_{n-1})。

    max_k, dressing, alternate, drop は負の対照のための引数（既定値が正しい式）。
    dressing = 'plus' は、符号 (-1)^{...} の代わりに cup-1 の項を + の符号で足した式
    （alpha = prod b_i(e_i) * (1/2 + sum b_j(e_k))。N <= 4 では正しい式と同じ演算子、N >= 5 では誤り）。
    """
    n = lat.n
    terms = []
    for k in range(n if max_k is None else max_k + 1):
        if k in drop:
            continue
        colors = [0] + list(range(k + 1, n))
        sign_k = (-1) ** k if alternate else 1
        for G, sgn in lat.sigma[k].items():
            coef = sign_k * sgn * (PI_UNIT >> (k + 1))
            if dressing == 'plus':
                c0, fac, extra = alpha_term(lat, G, colors, coef, True)
                terms.append((c0, fac, []))
                terms += [(2 * c0, fac + [x], []) for x in extra]
            else:
                terms.append(alpha_term(lat, G, colors, coef, bool(dressing)))
    return terms


def gate_inventory(lat):
    """W を構成する物理ゲートの種類と個数。各項は「制御 m-1 個の位相ゲート（角度 pi/2^(k+1)）」。"""
    rows = []
    for k in range(lat.n):
        m = lat.n - k
        rows.append(dict(stratum=k, dim=m, n_gates=len(lat.sigma[k]), qubits_per_gate=m,
                         angle_denominator=2 ** (k + 1), hierarchy_level=(m - 1) + (k + 1) + 1,
                         sign_dressing_qubits=(m - 1) * (m - 2) // 2))
    return rows


def eval_terms(terms, cfg):
    """項の列を配位の集合 cfg の上で評価する。戻り値は pi/2^Q 単位の整数（mod 2^(Q+1)）。"""
    out = np.zeros(cfg.shape, dtype=np.int64)
    for coef, fac, sgn in terms:
        prod = cfg.get(*fac[0]).copy()
        for f in fac[1:]:
            prod &= cfg.get(*f)
        if sgn:
            par = cfg.get(*sgn[0]).copy()
            for f in sgn[1:]:
                par ^= cfg.get(*f)
            out += coef * (prod.astype(np.int64) * (1 - 2 * par.astype(np.int64)))
        else:
            out += coef * prod.astype(np.int64)
    return out % MOD


def terms_support(terms):
    return sorted({f for _, fac, sgn in terms for f in fac + sgn})


# ------------------------------------------------------------------------------------------------------
# Z 型の条件を満たす配位の空間
# ------------------------------------------------------------------------------------------------------
class Sector:
    """平坦（da = 0）で境界条件を満たす配位。a = m * (論理 1 の代表) + sum_g z_g * (ゲージ変換 g)。

    座標 z のビット 0 が論理値 m、ビット 1.. がゲージ変換の生成元。A[c, e, bit] が a_c(e) への寄与。
    """

    def __init__(self, lat):
        self.lat = lat
        n, s = lat.n, lat.s
        self.gens = lat.gauge_generators()
        self.D = 1 + len(self.gens)
        self.bit = {g: 1 + i for i, g in enumerate(self.gens)}
        A = np.zeros((lat.N, lat.E, self.D), dtype=np.uint8)
        # 論理 1 の代表：a_j = d(lambda_j)、lambda_j(v) = [x_j = L_j かつ i<j で x_i < L_i]
        for j in range(n):
            lam = [int(v[j] == lat.L[j] and all(v[i] < lat.L[i] for i in range(j))) for v in lat.verts]
            for e, (u, w) in enumerate(lat.edges):
                A[j, e, 0] = lam[u] ^ lam[w]
        for g, b in self.bit.items():
            v, cols = g
            for e, (u, w) in enumerate(lat.edges):
                if v in (u, w):
                    for c in cols:
                        A[c, e, b] ^= 1
        self.A = A
        self.special_bits = [self.bit[g] for g in self.gens if g[1] == (s,)]
        self.special_vertex = {self.bit[g]: g[0] for g in self.gens if g[1] == (s,)}
        # V（a_s -> a_s + sum_j a_j）の z への作用：頂点 v（B_N の外）の s のビットに、m と v の普通の色のビットを足す
        self.V_rule = []
        for g in self.gens:
            if g[1] == (s,):
                v = g[0]
                src = [0] + [self.bit[(v, (j,))] for j in lat.alive_colors(v)]
                self.V_rule.append((self.bit[g], src))
        # 生成元に対応する演算子（位相の項と、途中のずらし）
        self.gen_ops = {g: self._make_op(g) for g in self.gens}

    def shift_of(self, v, cols):
        t = np.zeros((self.lat.N, self.lat.E), dtype=np.uint8)
        for e, (u, w) in enumerate(self.lat.edges):
            if v in (u, w):
                for c in cols:
                    t[c, e] ^= 1
        return t

    def _make_op(self, g):
        """生成元 (v, 色の組) の演算子 = S^{c1}_v S^{c2}_v ...（右から順に作用）。"""
        v, cols = g
        pieces, acc = [], np.zeros((self.lat.N, self.lat.E), dtype=np.uint8)
        for c in cols:
            pieces.append((stabilizer_terms(self.lat, c, v), acc.copy()))
            acc ^= self.shift_of(v, (c,))
        return Op(pieces, acc, 1 << self.bit[g])

    def check_columns(self):
        """A の各列が平坦で境界条件を満たすこと。"""
        lat = self.lat
        for b in range(self.D):
            a = self.A[:, :, b]
            for (u, v, w) in lat.simplices.get(2, []):
                if np.any(a[:, lat.eid[(u, v)]] ^ a[:, lat.eid[(v, w)]] ^ a[:, lat.eid[(u, w)]]):
                    return False
            for e, ed in enumerate(lat.edges):
                for i in range(lat.n):
                    if lat.in_B(i, ed) and a[i, e]:
                        return False
                if lat.in_BN(ed) and (a[lat.s, e] or a[:lat.n, e].sum() % 2):
                    return False
        return True

    def apply_V_bits(self, Z):
        """Z: (S, D) の 0/1 配列。V を作用させた座標を返す。"""
        Z2 = Z.copy()
        for tb, src in self.V_rule:
            Z2[:, tb] ^= Z[:, src].sum(axis=1).astype(np.uint8) & 1
        return Z2


class Op:
    """|a> -> exp(i pi f(a)) |a + shift>。f(a) = sum_i terms_i(a + offset_i)。"""

    def __init__(self, pieces, shift, zmask=None):
        self.pieces = pieces
        self.shift = shift
        self.zmask = zmask

    def phase(self, cfg):
        out = np.zeros(cfg.shape, dtype=np.int64)
        for terms, off in self.pieces:
            out += eval_terms(terms, cfg.shifted(off) if off.any() else cfg)
        return out % MOD


def logical_dimension(lat):
    """Z 型の条件（平坦＋境界条件）の解空間の次元から、ゲージ変換の生成元の数を引いたもの = 論理量子ビット数。

    辺の変数 a_c(e) 全てについての GF(2) の連立方程式を直接解く（Sector の構成とは独立）。
    """
    N, E, n, s = lat.N, lat.E, lat.n, lat.s
    rows = []
    for (u, v, w) in lat.simplices.get(2, []):
        for c in range(N):
            rows.append((1 << (c * E + lat.eid[(u, v)])) | (1 << (c * E + lat.eid[(v, w)])) | (1 << (c * E + lat.eid[(u, w)])))
    for e, ed in enumerate(lat.edges):
        for i in range(n):
            if lat.in_B(i, ed):
                rows.append(1 << (i * E + e))
        if lat.in_BN(ed):
            rows.append(1 << (s * E + e))
            rows.append(sum(1 << (j * E + e) for j in range(n)))
    rank = _gf2_rank(rows)
    gens = lat.gauge_generators()
    cols = []
    for v, cs in gens:
        x = 0
        for e, (u, w) in enumerate(lat.edges):
            if v in (u, w):
                for c in cs:
                    x ^= 1 << (c * E + e)
        cols.append(x)
    return dict(n_variables=N * E, rank_constraints=rank, dim_solutions=N * E - rank, n_gauge=len(gens),
                rank_gauge=_gf2_rank(cols), k_logical=N * E - rank - _gf2_rank(cols))


def _gf2_rank(rows):
    basis = {}
    for r in rows:
        while r:
            h = r.bit_length() - 1
            if h in basis:
                r ^= basis[h]
            else:
                basis[h] = r
                break
    return len(basis)


# ------------------------------------------------------------------------------------------------------
# 配位の集合
# ------------------------------------------------------------------------------------------------------
class SampleConfig:
    """無作為に選んだ配位。a は (S, N, E) の 0/1 配列。"""

    def __init__(self, a):
        self.a = a
        self.shape = (a.shape[0],)

    @classmethod
    def from_bits(cls, sector, Z):
        A = sector.A.reshape(-1, sector.D).astype(np.int64)
        a = (Z.astype(np.int64) @ A.T) % 2
        return cls(a.astype(np.uint8).reshape(Z.shape[0], sector.lat.N, sector.lat.E))

    def get(self, c, e):
        return self.a[:, c, e]

    def shifted(self, t):
        return SampleConfig(self.a ^ t[None])


class BasisConfig:
    """2^D 個の基底状態全て。a_c(e) = parity(z & mask[c][e]) ^ offset[c][e]。"""

    def __init__(self, masks, D, offset=None, cache=None, cache_limit=2 ** 30):
        self.masks, self.D = masks, D
        self.shape = (1 << D,)
        self.offset = offset
        self._cache = {} if cache is None else cache
        self._limit = cache_limit

    def _raw(self, mask):
        arr = self._cache.get(mask)
        if arr is None:
            arr = np.zeros(1, dtype=np.uint8)
            for b in range(self.D):
                arr = np.concatenate([arr, arr ^ ((mask >> b) & 1)]) if (mask >> b) & 1 else np.concatenate([arr, arr])
            if (len(self._cache) + 1) * arr.nbytes > self._limit:
                self._cache.clear()
            self._cache[mask] = arr
        return arr

    def get(self, c, e):
        arr = self._raw(self.masks[c][e])
        if self.offset is not None and self.offset[c, e]:
            return arr ^ 1
        return arr

    def shifted(self, t):
        off = t if self.offset is None else (self.offset ^ t)
        return BasisConfig(self.masks, self.D, off, self._cache, self._limit)


def sector_masks(sector):
    lat = sector.lat
    w = 1 << np.arange(sector.D, dtype=object)
    return [[int((sector.A[c, e].astype(object) * w).sum()) for e in range(lat.E)] for c in range(lat.N)]


# ------------------------------------------------------------------------------------------------------
# 恒等式の検査（無作為な配位。格子の大きさに制限なし）
# ------------------------------------------------------------------------------------------------------
class Checker:
    def __init__(self, lat, n_samples=64, seed=0, w_terms=None, use_V=True):
        self.lat = lat
        self.sec = Sector(lat)
        self.rng = np.random.default_rng(seed)
        self.Z = self.rng.integers(0, 2, size=(n_samples, self.sec.D), dtype=np.uint8)
        self.cfg = SampleConfig.from_bits(self.sec, self.Z)
        self.wt = W_terms(lat) if w_terms is None else w_terms
        self.use_V = use_V

    def _V(self, Z):
        return self.sec.apply_V_bits(Z) if self.use_V else Z.copy()

    def stabilizers_square_to_one(self):
        """各生成元 S について S^2 = 1（平坦な配位の上で）。不一致の数を返す。"""
        bad = 0
        for g, op in self.sec.gen_ops.items():
            bad += int(np.count_nonzero((op.phase(self.cfg) + op.phase(self.cfg.shifted(op.shift))) % MOD))
        return bad

    def stabilizers_commute(self, max_pairs=4000):
        """生成元の対が可換であること。台が交わる対だけを調べる。"""
        gens = list(self.sec.gen_ops.items())
        sup = {g: {e for terms, _ in op.pieces for (_, e) in terms_support(terms)} | set(np.nonzero(op.shift.any(axis=0))[0])
               for g, op in gens}
        pairs = [(i, j) for i in range(len(gens)) for j in range(i + 1, len(gens)) if sup[gens[i][0]] & sup[gens[j][0]]]
        if len(pairs) > max_pairs:
            idx = self.rng.choice(len(pairs), size=max_pairs, replace=False)
            pairs = [pairs[i] for i in idx]
        bad = 0
        for i, j in pairs:
            o1, o2 = gens[i][1], gens[j][1]
            lhs = o2.phase(self.cfg) + o1.phase(self.cfg.shifted(o2.shift))        # S1 S2
            rhs = o1.phase(self.cfg) + o2.phase(self.cfg.shifted(o1.shift))        # S2 S1
            bad += int(np.count_nonzero((lhs - rhs) % MOD))
        return bad, len(pairs)

    def target_op(self, g):
        """U S_g U^dagger が等しくなるべき安定化子。B_N の外の普通の色 j：S^j S^s。それ以外：S_g 自身。"""
        v, cols = g
        s = self.lat.s
        if (not self.lat.on_BN_v[v]) and cols != (s,) and self.use_V:
            o1, o2 = self.sec.gen_ops[g], self.sec.gen_ops[(v, (s,))]
            return Op(o1.pieces + [(o2.pieces[0][0], o1.shift.copy())], o1.shift ^ o2.shift)
        return self.sec.gen_ops[g]

    def covariance(self):
        """U S_g U^dagger = S'_g を全ての生成元について調べる。(不一致のある生成元の数, 生成元の数)"""
        cfgV = SampleConfig.from_bits(self.sec, self._V(self.Z))
        w0 = eval_terms(self.wt, self.cfg)
        bad = 0
        for g, op in self.sec.gen_ops.items():
            tgt = self.target_op(g)
            lhs = eval_terms(self.wt, self.cfg.shifted(tgt.shift)) - w0 + op.phase(cfgV)
            bad += int(np.any((lhs - tgt.phase(self.cfg)) % MOD))
        return bad, len(self.sec.gen_ops)

    def logical_phase(self, n_configs=8):
        """U の論理作用。theta_m = exp(i pi [w(Va) - (a から Va までの S^s の位相の和)])。

        戻り値：m = 0, 1 それぞれについて、配位ごとの theta（pi/2^Q 単位）の集合。1 元集合なら配位によらない。
        """
        sec, lat = self.sec, self.lat
        out = {0: set(), 1: set()}
        for i in range(min(n_configs, self.Z.shape[0])):
            for m in (0, 1):
                z = self.Z[i:i + 1].copy()
                z[0, 0] = m
                zV = self._V(z)
                w = int(eval_terms(self.wt, SampleConfig.from_bits(sec, zV))[0])
                cur, acc = z.copy(), 0
                for b in sec.special_bits:
                    if cur[0, b] != zV[0, b]:
                        op = sec.gen_ops[(sec.special_vertex[b], (lat.s,))]
                        acc += int(op.phase(SampleConfig.from_bits(sec, cur))[0])
                        cur[0, b] ^= 1
                out[m].add((w - acc) % MOD)
        return out

    def summary(self):
        sq = self.stabilizers_square_to_one()
        cm, npairs = self.stabilizers_commute()
        cov, ngen = self.covariance()
        lp = self.logical_phase()
        well = len(lp[0]) == 1 and len(lp[1]) == 1
        rel = ((min(lp[1]) - min(lp[0])) % MOD) if well else None
        return dict(N=self.lat.N, L=self.lat.L, D=self.sec.D, n_generators=ngen, square_violations=sq,
                    commute_violations=cm, commute_pairs=npairs, covariance_violations=cov,
                    logical_phase_well_defined=well, logical_phase_units=rel,
                    logical_phase_over_pi=(None if rel is None else phase_fraction(rel)))


def phase_fraction(units):
    """pi/2^Q 単位の整数を、(-1, 1] の範囲の分数の文字列にする（pi の倍数）。"""
    u = units % MOD
    if u > PI_UNIT:
        u -= MOD
    if u == 0:
        return '0'
    g = math.gcd(abs(u), PI_UNIT)
    num, den = u // g, PI_UNIT // g
    return f'{num}/{den}' if den != 1 else f'{num}'


def expected_phase_units(N):
    """R_N = diag(1, exp(2 pi i / 2^N)) の位相 2 pi / 2^N = pi / 2^(N-1) を pi/2^Q 単位で。

    この格子の向きの取り方では U = W V は R_N として作用する（[KZH] の記法では T^dagger。向きの規約の違い）。
    """
    return (PI_UNIT >> (N - 1)) % MOD


# ------------------------------------------------------------------------------------------------------
# 状態ベクトルによる code switching の実行（小さい格子）
# ------------------------------------------------------------------------------------------------------
_PHASE_TABLE = np.exp(1j * np.pi * np.arange(MOD) / PI_UNIT)


class StateSim:
    """Sector の座標 z の上の状態ベクトル。次元 2^D。"""

    def __init__(self, lat, w_terms=None, max_D=24):
        self.lat = lat
        self.sec = Sector(lat)
        self.D = self.sec.D
        if self.D > max_D:
            raise MemoryError(f'D = {self.D} > max_D = {max_D}')
        self.cfg = BasisConfig(sector_masks(self.sec), self.D, cache_limit=2 ** 29)
        self.wt = W_terms(lat) if w_terms is None else w_terms
        self._gen_phase = {}
        self._V_index = None
        self._w_phase = None

    # --- 基本操作 ---
    def _flip(self, psi, zmask):
        view = psi.reshape([2] * self.D)
        axes = [self.D - 1 - b for b in range(self.D) if (zmask >> b) & 1]
        return np.flip(view, axis=axes).reshape(-1)

    def gen_phase(self, g):
        """生成元の位相。メモリを抑えるため、pi/2^Q 単位の整数（uint16）で持ち、使うときに複素数にする。"""
        if g not in self._gen_phase:
            self._gen_phase[g] = self.sec.gen_ops[g].phase(self.cfg).astype(np.uint16)
        return _PHASE_TABLE[self._gen_phase[g]]

    def apply_gen(self, psi, g):
        return np.ascontiguousarray(self._flip(self.gen_phase(g) * psi, self.sec.gen_ops[g].zmask))

    def measure_gen(self, psi, g, rng, force=None):
        """S_g を測る（Kraus 演算子 (1 +- S)/2）。戻り値 (結果 0/1, 測定後の状態, 結果 0 の確率)。"""
        Sp = self.apply_gen(psi, g)
        p0 = float(np.clip(0.5 * (1 + np.vdot(psi, Sp).real), 0, 1))
        out = (0 if rng.random() < p0 else 1) if force is None else force
        new = psi + Sp if out == 0 else psi - Sp
        nrm = np.linalg.norm(new)
        return out, new / nrm, p0

    def expect_gen(self, psi, g):
        return float(np.vdot(psi, self.apply_gen(psi, g)).real)

    def V_index(self):
        if self._V_index is None:
            idx = np.arange(1 << self.D, dtype=np.int64)
            for tb, src in self.sec.V_rule:
                mask = sum(1 << b for b in src)
                idx ^= self.cfg._raw(mask).astype(np.int64) << tb
            self._V_index = idx
        return self._V_index

    def w_phase(self):
        if self._w_phase is None:
            self._w_phase = eval_terms(self.wt, self.cfg).astype(np.uint16)
        return _PHASE_TABLE[self._w_phase]

    def apply_U(self, psi, use_V=True):
        if use_V:
            psi = psi[self.V_index()]            # V は対合（V^2 = 1）
        return self.w_phase() * psi

    def z_string_phase(self, v, colors):
        """頂点 v から x_0 方向に B_N まで伸ばした Z の弦（色 colors）。対角で ±1。"""
        lat = self.lat
        par = np.zeros(1 << self.D, dtype=np.uint8)
        x = list(lat.verts[v])
        while x[0] < lat.L[0]:
            u = lat.vid[tuple(x)]
            x[0] += 1
            e = lat.eid[(u, lat.vid[tuple(x)])]
            for c in colors:
                par ^= self.cfg.get(c, e)
        return 1.0 - 2.0 * par

    # --- 状態 ---
    def pauli_plus(self):
        """Pauli 符号（n 枚のトーリック符号を B_N で貼り合わせたもの）の |+> と、特別な色の |0...0>。"""
        psi = np.ones(1 << self.D, dtype=np.complex128)
        for b in self.sec.special_bits:
            psi = psi * (1 - self.cfg._raw(1 << b))
        return psi / np.linalg.norm(psi)

    def target(self, phase_units):
        """diag(1, exp(i pi phase_units / 2^Q)) |+>。"""
        m = self.cfg._raw(1).astype(np.int64)
        return self.pauli_plus() * _PHASE_TABLE[(phase_units * m) % MOD]

    def code_basis(self):
        """階層 N の符号の論理基底 |0>, |1>（全ての安定化子の +1 固有状態への射影で作る）。"""
        out = []
        for m in (0, 1):
            psi = np.zeros(1 << self.D, dtype=np.complex128)
            psi[m] = 1.0
            for g in self.sec.gens:
                psi = psi + self.apply_gen(psi, g)
                psi /= np.linalg.norm(psi)
            out.append(psi)
        return out

    def logical_matrix(self, use_V=True):
        b = self.code_basis()
        stab = min(self.expect_gen(x, g) for x in b for g in self.sec.gens)
        Ub = [self.apply_U(x, use_V) for x in b]
        M = np.array([[np.vdot(b[i], Ub[j]) for j in range(2)] for i in range(2)])
        leak = max(abs(1 - np.linalg.norm(M[:, j])) for j in range(2))
        return M, leak, stab

    # --- プロトコル ---
    def run_protocol(self, rng, charge_mode='fix_before_U', use_V=True, skip_out_correction=False):
        """switch-in -> U -> switch-out。出力と R_N |+> の忠実度などを返す。

        charge_mode = 'fix_before_U'：switch-in の測定結果 -1（電荷）を、U の前に色 s の Z の弦で消す
                      'frame'       ：消さずに U を通し、switch-out の後で普通の色の Z の弦（Pauli フレーム）で消す
                      'none'        ：消さない（負の対照）
        skip_out_correction = True：switch-out の補正（C^{N-2}Z）をかけない（負の対照）
        """
        lat, sec, s = self.lat, self.sec, self.lat.s
        sgens = [g for g in sec.gens if g[1] == (s,)]
        ogens = [g for g in sec.gens if g[1] != (s,)]
        psi = self.pauli_plus()
        # 1. switch-in：S^s_v を測る
        outcomes, probs = {}, []
        for g in sgens:
            o, psi, p0 = self.measure_gen(psi, g, rng)
            outcomes[g[0]] = o
            probs.append(p0)
        other_ok = min([self.expect_gen(psi, g) for g in ogens], default=1.0)
        charged = [v for v, o in outcomes.items() if o]
        if charge_mode == 'fix_before_U':
            for v in charged:
                psi = psi * self.z_string_phase(v, [s])
        in_code = min([self.expect_gen(psi, g) for g in sec.gens], default=1.0) if charge_mode == 'fix_before_U' else None
        # 2. 論理ゲート
        psi = self.apply_U(psi, use_V)
        after_U = min([self.expect_gen(psi, g) for g in sec.gens], default=1.0) if charge_mode == 'fix_before_U' else None
        # 3. switch-out：色 s の Z を全ての辺で測る（= s のゲージ変換のビットを読む）
        pr = np.abs(psi) ** 2
        zsample = int(rng.choice(pr.size, p=pr / pr.sum()))
        keep = np.ones(pr.size, dtype=bool)
        flips = []
        for b in sec.special_bits:
            bitarr = self.cfg._raw(1 << b)
            val = (zsample >> b) & 1
            keep &= bitarr == val
            if val:
                flips.append(b)
        psi = np.where(keep, psi, 0)
        psi /= np.linalg.norm(psi)
        # 4. 補正：読んだ配位 a_s = d(lambda) に対して prod_v (S^s_v)^{lambda_v}（X^s と、普通の色への C^{N-2}Z）
        n_corr_gates = 0
        for b in flips:
            g = (sec.special_vertex[b], (s,))
            n_corr_gates += len(sec.gen_ops[g].pieces[0][0])
            if skip_out_correction:                          # X^s だけかけて、C^{N-2}Z を省く
                psi = np.ascontiguousarray(self._flip(psi, sec.gen_ops[g].zmask))
            else:
                psi = self.apply_gen(psi, g)
        if charge_mode == 'frame':
            for v in charged:
                psi = psi * self.z_string_phase(v, list(range(lat.n)))
        fid = float(abs(np.vdot(self.target(expected_phase_units(lat.N)), psi)) ** 2)
        fid_wrong = float(abs(np.vdot(self.target(0), psi)) ** 2)
        return dict(fidelity=fid, fidelity_to_plus=fid_wrong, n_measured=len(sgens), n_charges=len(charged),
                    n_flux_out=len(flips), n_correction_gates=n_corr_gates, prob0_min=min(probs, default=0.5), prob0_max=max(probs, default=0.5),
                    other_stabilizers_after_in=other_ok, in_code_before_U=in_code, in_code_after_U=after_U)


# ------------------------------------------------------------------------------------------------------
# 独立な実装：辺の量子ビットを全て持つ（ごく小さい格子だけ）。Sector を使わない
# ------------------------------------------------------------------------------------------------------
class DenseSim:
    """量子ビット (c, e) を全て持つ状態ベクトル（N*E <= 22 程度まで）。Sector の構成を使わない検算。"""

    def __init__(self, lat, max_qubits=22):
        self.lat = lat
        self.nq = lat.N * lat.E
        if self.nq > max_qubits:
            raise MemoryError(f'{self.nq} qubits')
        masks = [[1 << (c * lat.E + e) for e in range(lat.E)] for c in range(lat.N)]
        self.cfg = BasisConfig(masks, self.nq)
        self.wt = W_terms(lat)

    def bit(self, c, e):
        return self.cfg.get(c, e)

    def valid(self):
        """平坦かつ境界条件を満たす配位の指示関数。"""
        lat = self.lat
        ok = np.ones(1 << self.nq, dtype=bool)
        for (u, v, w) in lat.simplices.get(2, []):
            for c in range(lat.N):
                ok &= (self.bit(c, lat.eid[(u, v)]) ^ self.bit(c, lat.eid[(v, w)]) ^ self.bit(c, lat.eid[(u, w)])) == 0
        for e, ed in enumerate(lat.edges):
            for i in range(lat.n):
                if lat.in_B(i, ed):
                    ok &= self.bit(i, e) == 0
            if lat.in_BN(ed):
                ok &= self.bit(lat.s, e) == 0
                par = np.zeros(1 << self.nq, dtype=np.uint8)
                for j in range(lat.n):
                    par ^= self.bit(j, e)
                ok &= par == 0
        return ok

    def _flip(self, psi, t):
        axes = [self.nq - 1 - (c * self.lat.E + e) for c in range(self.lat.N) for e in range(self.lat.E) if t[c, e]]
        return np.flip(psi.reshape([2] * self.nq), axis=axes).reshape(-1)

    def apply_S(self, psi, c, v):
        ph = _PHASE_TABLE[eval_terms(stabilizer_terms(self.lat, c, v), self.cfg)]
        t = np.zeros((self.lat.N, self.lat.E), dtype=np.uint8)
        for e, (u, w) in enumerate(self.lat.edges):
            if v in (u, w):
                t[c, e] = 1
        return np.ascontiguousarray(self._flip(ph * psi, t))

    def logical_bit(self):
        """論理 Z：x_0 軸に沿った色 0 の Z の弦。"""
        lat = self.lat
        par = np.zeros(1 << self.nq, dtype=np.uint8)
        x = [0] * lat.n
        while x[0] < lat.L[0]:
            u = lat.vid[tuple(x)]
            x[0] += 1
            par ^= self.bit(0, lat.eid[(u, lat.vid[tuple(x)])])
        return par

    def run_protocol(self, rng):
        lat, s = self.lat, self.lat.s
        ok = self.valid()
        a_s_zero = np.ones(1 << self.nq, dtype=bool)
        for e in range(lat.E):
            a_s_zero &= self.bit(s, e) == 0
        psi0 = (ok & a_s_zero).astype(np.complex128)
        n_valid_pauli = int(round(psi0.real.sum()))
        psi = psi0 / np.linalg.norm(psi0)
        outside = [v for v in range(lat.V) if not lat.on_BN_v[v]]
        charged = []
        for v in outside:
            Sp = self.apply_S(psi, s, v)
            p0 = 0.5 * (1 + np.vdot(psi, Sp).real)
            o = 0 if rng.random() < p0 else 1
            psi = psi + Sp if o == 0 else psi - Sp
            psi /= np.linalg.norm(psi)
            if o:
                charged.append(v)
        for v in charged:                                   # 電荷を色 s の Z の弦で消す
            x = list(lat.verts[v])
            par = np.zeros(1 << self.nq, dtype=np.uint8)
            while x[0] < lat.L[0]:
                u = lat.vid[tuple(x)]
                x[0] += 1
                par ^= self.bit(s, lat.eid[(u, lat.vid[tuple(x)])])
            psi = psi * (1.0 - 2.0 * par)
        # U = W V。V は a_s に普通の色の和を足す
        idx = np.arange(1 << self.nq, dtype=np.int64)
        for e in range(lat.E):
            par = np.zeros(1 << self.nq, dtype=np.uint8)
            for j in range(lat.n):
                par ^= self.bit(j, e)
            idx ^= par.astype(np.int64) << (s * lat.E + e)
        psi = _PHASE_TABLE[eval_terms(self.wt, self.cfg)] * psi[idx]
        leak = float(1 - np.sum(np.abs(psi[ok]) ** 2))
        # switch-out：色 s を全ての辺で測る
        pr = np.abs(psi) ** 2
        zs = int(rng.choice(pr.size, p=pr / pr.sum()))
        a_s = [(zs >> (s * lat.E + e)) & 1 for e in range(lat.E)]
        keep = np.ones(pr.size, dtype=bool)
        for e in range(lat.E):
            keep &= self.bit(s, e) == a_s[e]
        psi = np.where(keep, psi, 0)
        psi /= np.linalg.norm(psi)
        # a_s = d(lambda)、lambda は B_N で 0。B_N から辺をたどって lambda を決める
        lam = {v: 0 for v in range(lat.V) if lat.on_BN_v[v]}
        changed = True
        while changed:
            changed = False
            for e, (u, w) in enumerate(lat.edges):
                if u in lam and w not in lam:
                    lam[w] = lam[u] ^ a_s[e]
                    changed = True
                elif w in lam and u not in lam:
                    lam[u] = lam[w] ^ a_s[e]
                    changed = True
        consistent = all(lam[u] ^ lam[w] == a_s[e] for e, (u, w) in enumerate(lat.edges))
        for v in outside:
            if lam[v]:
                psi = self.apply_S(psi, s, v)
        tgt = psi0 * _PHASE_TABLE[(expected_phase_units(lat.N) * self.logical_bit().astype(np.int64)) % MOD]
        tgt /= np.linalg.norm(tgt)
        return dict(fidelity=float(abs(np.vdot(tgt, psi)) ** 2), leak_after_U=leak, n_valid_pauli=n_valid_pauli,
                    outcome_consistent=bool(consistent), n_charges=len(charged))


# ------------------------------------------------------------------------------------------------------
# Pauli 符号（switch-in の前と switch-out の後の符号）の距離。整数計画法（scipy.optimize.milp）
# ------------------------------------------------------------------------------------------------------
def pauli_code_distances(lat, time_limit=120.0):
    """n 枚のトーリック符号を B_N で貼り合わせた Pauli 符号の [[n, 1, (d_X, d_Z)]]。

    d_X = 論理 X の最小の重み = 論理 1 の類に属する配位の最小の重み（特別な色は使わない）
    d_Z = 論理 Z の最小の重み = 全てのゲージ変換と可換で、論理 1 の代表と反可換な Z の積の最小の重み
    戻り値の *_optimal が False のときは時間切れで、値は上界。
    """
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import lil_matrix
    sec = Sector(lat)
    n, E = lat.n, lat.E
    nbits = [0] + [sec.bit[g] for g in sec.gens if g[1] != (lat.s,)]
    A = sec.A[:n].reshape(n * E, sec.D)[:, nbits].astype(np.int64)
    rows = np.nonzero(A.any(axis=1))[0]
    A = A[rows]
    nq, nb = A.shape
    out = dict(n_qubits=int(nq))
    # d_X：変数 [z_1..z_{nb-1}, a_1..a_nq, k_1..k_nq]。A z - a - 2k = 0、z_0 = 1
    nv = (nb - 1) + nq + nq
    M = lil_matrix((nq, nv))
    M[:, :nb - 1] = A[:, 1:]
    for q in range(nq):
        M[q, nb - 1 + q] = -1
        M[q, nb - 1 + nq + q] = -2
    c = np.zeros(nv)
    c[nb - 1:nb - 1 + nq] = 1
    ub = np.ones(nv)
    ub[nb - 1 + nq:] = nb
    res = milp(c, constraints=LinearConstraint(M.tocsr(), -A[:, 0], -A[:, 0]), integrality=np.ones(nv),
               bounds=Bounds(np.zeros(nv), ub), options=dict(time_limit=time_limit))
    out.update(d_X=int(round(res.fun)) if res.x is not None else None, d_X_optimal=bool(res.status == 0))
    # d_Z：変数 [r_1..r_nq, k_0..k_{nb-1}]。A^T r - 2k = (1, 0, ..., 0)
    nv = nq + nb
    M = lil_matrix((nb, nv))
    M[:, :nq] = A.T
    for b in range(nb):
        M[b, nq + b] = -2
    rhs = np.zeros(nb)
    rhs[0] = 1
    c = np.zeros(nv)
    c[:nq] = 1
    ub = np.ones(nv)
    ub[nq:] = nq
    res = milp(c, constraints=LinearConstraint(M.tocsr(), rhs, rhs), integrality=np.ones(nv),
               bounds=Bounds(np.zeros(nv), ub), options=dict(time_limit=time_limit))
    out.update(d_Z=int(round(res.fun)) if res.x is not None else None, d_Z_optimal=bool(res.status == 0))
    return out


# ------------------------------------------------------------------------------------------------------
# 資源の数え上げ
# ------------------------------------------------------------------------------------------------------
def resource_row(lat):
    """量子ビット数、安定化子の重み、W のゲート数、X 誤りが U を通って広がる量子ビット数。"""
    sec = Sector(lat)
    qc = lat.qubit_counts()
    s = lat.s
    xw, dress, dress_q = [], [], []
    for v in range(lat.V):
        if lat.on_BN_v[v]:
            continue
        deg = sum(1 for (u, w) in lat.edges if v in (u, w))
        t = stabilizer_terms(lat, s, v)
        xw.append(deg)
        dress.append(len(t))
        dress_q.append(len(terms_support(t)))
    wt = W_terms(lat)
    touch = {}
    for _, fac, sgn in wt:
        sup = set(fac + sgn)
        for f in fac + sgn:
            touch.setdefault(f, set()).update(sup)
    spread = [len(v) for v in touch.values()]
    per_q = {}
    for _, fac, sgn in wt:
        for f in fac:
            per_q[f] = per_q.get(f, 0) + 1
    inv = gate_inventory(lat)
    return dict(N=lat.N, L='x'.join(map(str, lat.L)), dim=lat.n, vertices=lat.V, edges=lat.E, qubits=qc['total'],
                qubits_pauli_code=qc['pauli_code'], sector_dim_D=sec.D, n_switch_in_checks=len(xw),
                switch_in_check_X_weight_max=max(xw, default=0), switch_in_check_dressing_gates_max=max(dress, default=0),
                switch_in_check_dressing_qubits_max=max(dress_q, default=0),
                dressing_gate_qubits=lat.N - 1, W_gates_total=len(wt), W_gates_bulk=inv[0]['n_gates'],
                W_gates_last_stratum=inv[-1]['n_gates'], W_gates_per_qubit_max=max(per_q.values(), default=0),
                X_error_spread_max=max(spread, default=0), X_error_spread_mean=float(np.mean(spread)) if spread else 0.0)


# ------------------------------------------------------------------------------------------------------
# 群コチェインの恒等式（格子を使わない、W の式そのものの検査）
#   普通の色のゲージ群 Z_2^r（r = N-1）。k-コチェイン = k 個の群の元の関数。
#   (delta c)(g_1..g_{k+1}) = c(g_2..) + sum_i (-1)^i c(.., g_i + g_{i+1}, ..) + (-1)^{k+1} c(g_1..g_k)
# ------------------------------------------------------------------------------------------------------
def _alpha_points(G, shift):
    """alpha_{k+1}(b_0..b_{k-1}) / 2^shift を点の列 G（形 (P, k)。G[:, i] は i 番目の引数の群の元）で評価する。"""
    k = G.shape[1]
    main = np.ones(G.shape[0], dtype=np.int64)
    for i in range(k):
        main *= (G[:, i] >> i) & 1
    sgn = np.zeros(G.shape[0], dtype=np.int64)
    for kk in range(1, k):
        for jj in range(kk + 1, k):
            sgn ^= (G[:, kk] >> jj) & 1
    return main * (PI_UNIT >> (shift + 1)) * (1 - 2 * sgn)


def _delta_points(F, G):
    """(delta F)(G)。F は (P, k) -> 値、G は (P, k+1)。"""
    k = G.shape[1] - 1
    out = F(G[:, 1:]).copy()
    for i in range(1, k + 1):
        merged = np.concatenate([G[:, :i - 1], (G[:, i - 1] ^ G[:, i])[:, None], G[:, i + 1:]], axis=1)
        out += (-1) ** i * F(merged)
    out += (-1) ** (k + 1) * F(G[:, :k])
    return out


def _points(n_bits, n_args, max_points, rng):
    total = (1 << n_bits) ** n_args
    if total <= max_points:
        idx = np.arange(total, dtype=np.int64)
        G = np.stack([(idx >> (n_bits * i)) & ((1 << n_bits) - 1) for i in range(n_args)], axis=1)
        return G, True
    return rng.integers(0, 1 << n_bits, size=(max_points, n_args), dtype=np.int64), False


def group_cochain_checks(N, max_points=2_000_000, seed=0):
    """W の式を支える恒等式を、群コチェインの水準で調べる。

    bulk    : delta alpha_N = (ねじれの変化) mod 2 pi                       （U がバルクで対称性であること）
    level k : alpha_{N-k} を「b_1 = 他の色の和」の部分群に制限したもの = (1/2) delta alpha_{N-k-1}  mod 2^(k+1) pi
              （Sigma_k の項の変化を Sigma_{k+1} の項が打ち消すこと。k = 0..N-3）
    戻り値：行のリスト（点の数、全点を調べたか、不一致の数）。
    """
    rng = np.random.default_rng(seed)
    r = N - 1
    rows = []
    # bulk
    G, ex = _points(r, r + 1, max_points, rng)
    lhs = _delta_points(lambda X: _alpha_points(X, 0), G)
    par = np.zeros(G.shape[0], dtype=np.int64)
    for j in range(r):
        par ^= (G[:, 1] >> j) & 1
    tgt = ((G[:, 0] >> 0) & 1) * par
    for j in range(1, r):
        tgt = tgt * ((G[:, j + 1] >> j) & 1)
    rows.append(dict(N=N, check='bulk', n_points=len(G), exhaustive=ex,
                     violations=int(np.count_nonzero((lhs - PI_UNIT * tgt) % MOD))))
    # 層の列
    for lev in range(0, N - 2):
        n = r - lev                                   # この層で生きている色の数（b_0..b_{n-1}）
        H, ex = _points(n - 1, n, max_points, rng)    # 部分群の座標（b_0, b_2, ..., b_{n-1}）
        par = np.zeros(H.shape, dtype=np.int64)
        for b in range(n - 1):
            par ^= (H >> b) & 1
        big = (H & 1) | (par << 1) | ((H >> 1) << 2)  # b_1 = 全体の和
        lhs = _alpha_points(big, lev)
        rhs = _delta_points(lambda X: _alpha_points(X, lev + 1), H)
        rows.append(dict(N=N, check=f'level {lev} -> {lev + 1}', n_points=len(H), exhaustive=ex,
                         violations=int(np.count_nonzero((lhs - rhs) % MOD))))
    return rows
