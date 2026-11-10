# ==================================================================================================
# V2 [KZH] の式との一致と、格子の向き
#   [KZH] が明示した W（単位 pi）
#     N=3： int_bulk a_r a_b / 2  -  int_{L_rb} a_r / 4
#     N=4： int_bulk [ a_r a_b a_g / 2 + a_r (a_g u_1 a_b) a_g ]  -  int_{bdry4} a_r a_g / 4  +  int_{hinge14} a_r / 8
#   本研究の式は、cup-1 の項を符号 (-1)^{...} として書いたもの。両者が全ての配位で同じ位相を与えることを確かめる。
#   色の対応：N=3 は (r, b) = (0, 1)、N=4 は (r, b, g) = (0, 1, 2)。
# ==================================================================================================
def kzh_terms(lat):
    """[KZH] の書き方での W の項（符号の修飾を使わず、cup-1 の項を別の項として足す）。"""
    e = lambda G, i: lat.eid[(G[i], G[i + 1])]
    terms = []
    if lat.N == 3:
        for G, sg in lat.sigma[0].items():
            terms.append((sg * (PI_UNIT // 2), [(0, e(G, 0)), (1, e(G, 1))], []))
        for G, sg in lat.sigma[1].items():
            terms.append((-sg * (PI_UNIT // 4), [(0, e(G, 0))], []))
    elif lat.N == 4:
        for G, sg in lat.sigma[0].items():
            terms.append((sg * (PI_UNIT // 2), [(0, e(G, 0)), (1, e(G, 1)), (2, e(G, 2))], []))
            terms.append((PI_UNIT, [(0, e(G, 0)), (2, e(G, 1)), (1, e(G, 1)), (2, e(G, 2))], []))     # a_r (a_g u_1 a_b) a_g
        for G, sg in lat.sigma[1].items():
            terms.append((-sg * (PI_UNIT // 4), [(0, e(G, 0)), (2, e(G, 1))], []))
        for G, sg in lat.sigma[2].items():
            terms.append((sg * (PI_UNIT // 8), [(0, e(G, 0))], []))
    return terms

ok, det = True, []
for N, L in [(3, (2, 2)), (3, (4, 3)), (4, (2, 2, 1)), (4, (3, 2, 2))]:
    lat = Lattice(N, L)
    ch = Checker(lat, n_samples=64, seed=SEED)
    same = int(np.count_nonzero((eval_terms(W_terms(lat), ch.cfg) - eval_terms(kzh_terms(lat), ch.cfg)) % MOD))
    full = Checker(lat, n_samples=N_SAMPLES, seed=SEED, w_terms=kzh_terms(lat)).summary()
    good = same == 0 and full['covariance_violations'] == 0 and full['logical_phase_units'] == expected_phase_units(N)
    ok &= good; det.append(f'N={N},L={L}:{"一致" if good else "不一致"}')
record('V2a [KZH] の N=3, 4 の式と一般式が同じ演算子', ok, '; '.join(det))

ok = all(Lattice(N, L).check_orientation() for N, L in [(2, (3,)), (3, (2, 3)), (4, (2, 2, 2)), (5, (2, 1, 1, 2)), (6, (1,) * 5)])
record('V2b 格子の向き（内部の面で符号が打ち消す）', ok)

ok, det = True, []
for N, L in [(2, (5,)), (3, (3, 3)), (4, (2, 2, 2)), (5, (1, 1, 1, 1)), (5, (2, 1, 1, 1))]:
    lat = Lattice(N, L); sec = Sector(lat); k = logical_dimension(lat)
    good = sec.check_columns() and k['k_logical'] == 1 and k['rank_gauge'] == k['n_gauge']
    ok &= good; det.append(f'N={N},L={L}:k={k["k_logical"]}')
record('V2c 配位空間の構成（平坦・境界条件・論理量子ビット 1 個・ゲージ変換が独立）', ok, '; '.join(det))
