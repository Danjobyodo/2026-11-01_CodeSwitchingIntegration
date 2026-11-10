# ==================================================================================================
# V5 独立な実装との一致
#   DenseSim は辺の量子ビットを全て持つ状態ベクトル（N x 辺の数 個の量子ビット）で、Sector（平坦な配位の座標）を使わない。
#   Z 型の条件を満たす配位を全数検査で選び、同じプロトコルを実行する。確認すること：
#     ・Pauli 符号の |+> の台の大きさ = 2^(D - 特別な色のビット数)（Sector の数え方と一致）
#     ・U の後も平坦・境界条件の空間に留まる（漏れ 0）
#     ・switch-out の測定結果が d(lambda) の形をしている
#     ・出力の忠実度 1
# ==================================================================================================
rng = np.random.default_rng(SEED)
ok, det = True, []
for N, L in V5_CASES:
    lat = Lattice(N, L); sec = Sector(lat); ds = DenseSim(lat)
    res = [ds.run_protocol(rng) for _ in range(V5_TRIALS)]
    expect = 2 ** (sec.D - len(sec.special_bits))
    good = all(r['fidelity'] > 1 - 1e-9 and r['leak_after_U'] < 1e-9 and r['outcome_consistent'] and r['n_valid_pauli'] == expect for r in res)
    ok &= good
    det.append(f'N={N},L={L}（{ds.nq} 量子ビット）:F最小={min(r["fidelity"] for r in res):.10f}')
record('V5 独立な実装（辺の量子ビットを全て持つ状態ベクトル）', ok, '; '.join(det))
