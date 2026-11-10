# ==================================================================================================
# V3 負の対照（格子の上の検査）：W の式の一部を壊すと、検査が失敗すること
#   正しい式        : 全て合格するはず
#   バルクだけ       : 境界の項（Sigma_1 以降）を全て落とす
#   最後の層を落とす  : 1 次元の層の項（R_N の位相を与える項）だけを落とす
#   符号を交互にしない: (-1/2)^k を (1/2)^k にする
#   修飾なし        : (-1)^{...} の符号（cup-1 に当たる項）を落とす。N=3 には修飾が無いので変わらない
#   cup-1 を + で足す: 符号の代わりに [KZH] の SM の形（cup-1 の項を + で足す）を全ての層に使う。N<=4 では正しい式と同じ、N>=5 で誤り
#   V なし          : W だけをかける
# ==================================================================================================
def verdict(lat, **kw):
    use_V = kw.pop('use_V', True)
    r = Checker(lat, n_samples=N_SAMPLES, seed=SEED, w_terms=W_terms(lat, **kw), use_V=use_V).summary()
    return r['covariance_violations'] == 0 and r['logical_phase_units'] == expected_phase_units(lat.N)

rows = []
for N, L in V3_CASES:
    lat = Lattice(N, L)
    rows.append(dict(N=N, L='x'.join(map(str, L)), 正しい式=verdict(lat), バルクだけ=verdict(lat, max_k=0),
                     最後の層を落とす=verdict(lat, drop=(lat.n - 1,)), 符号を交互にしない=verdict(lat, alternate=False),
                     修飾なし=verdict(lat, dressing=False), cup1_を足す=verdict(lat, dressing='plus'),
                     V_なし=verdict(lat, use_V=False)))
V3 = pd.DataFrame(rows)
display(V3)
bad_cols = ['バルクだけ', '最後の層を落とす', '符号を交互にしない', 'V_なし']
ok = V3['正しい式'].all() and (not V3[bad_cols].any().any()) and (not V3[V3.N >= 4]['修飾なし'].any()) and V3[V3.N == 3]['修飾なし'].all() \
     and V3[V3.N <= 4]['cup1_を足す'].all() and (not V3[V3.N >= 5]['cup1_を足す'].any())
record('V3 負の対照（式を壊すと検査が失敗する）', ok, f'{len(V3)} 個の格子 × 6 種類')
