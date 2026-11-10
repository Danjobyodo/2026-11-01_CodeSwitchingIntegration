# ==================================================================================================
# §1 符号と論理ゲートの検査
#   各格子について、無作為な N_SAMPLES 個の配位（平坦で境界条件を満たすゲージ場）の上で次を確かめる。
#     k_logical            : 論理量子ビットの数（Z 型の条件の解空間の次元 - ゲージ変換の数）。1 のはず
#     square / commute     : X 型安定化子が S^2 = 1 を満たし、互いに可換であること（不一致の数。0 のはず）
#     covariance           : U S U^dagger が安定化子であること（不一致のある生成元の数。0 のはず）
#     logical_phase        : U の論理作用 diag(1, exp(i pi x))。x = 1/2^(N-1) なら R_N
# ==================================================================================================
rows = []
for N, L in CASES['identity']:
    t0 = time.time()
    lat = Lattice(N, L)
    ch = Checker(lat, n_samples=N_SAMPLES, seed=SEED)
    r = ch.summary()
    k = logical_dimension(lat)['k_logical'] if lat.N * lat.E <= 20000 else None
    rows.append(dict(N=N, L='x'.join(map(str, L)), 空間次元=N - 1, 頂点=lat.V, 辺=lat.E, D=r['D'], k_logical=k,
                     square=r['square_violations'], commute=r['commute_violations'], 可換性を調べた対=r['commute_pairs'],
                     covariance=r['covariance_violations'], 生成元=r['n_generators'],
                     logical_phase=r['logical_phase_over_pi'], 期待値=phase_fraction(expected_phase_units(N)),
                     合格=bool(r['square_violations'] == 0 and r['commute_violations'] == 0 and r['covariance_violations'] == 0
                             and r['logical_phase_units'] == expected_phase_units(N) and k in (1, None)),
                     秒=round(time.time() - t0, 1)))
    print(rows[-1], flush=True)
IDENT = pd.DataFrame(rows)
IDENT.to_csv(os.path.join(OUT_DIR, 'study5_identity.csv'), index=False)
display(IDENT)
assert IDENT['合格'].all(), '§1 の検査に失敗した格子がある'
print('§1：全て合格。論理ゲートは R_N = diag(1, exp(2 pi i / 2^N))')
