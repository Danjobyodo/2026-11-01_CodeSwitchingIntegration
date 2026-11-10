# ==================================================================================================
# V4 負の対照（プロトコル）：補正を省くと出力が R_N |+> でなくなること
#   正しい手順        : 忠実度 1
#   switch-out 補正なし: 特別な色を測った後の C^(N-2)Z をかけない（X^s だけかける）
#   電荷を消さない     : switch-in の結果 -1 を放置する
#   どちらも「乱数がたまたま全て +1 / 補正のゲートが 0 個」の試行では忠実度 1 になるので、そうでない試行だけを数える。
#   （原点の S^s_v には C^(N-2)Z が付かないので、B_N の外の頂点が原点だけの格子 (1,...,1) はこの検査に使えない）
# ==================================================================================================
rng = np.random.default_rng(SEED)
rows = []
for N, L in V4_CASES:
    sim = StateSim(Lattice(N, L))
    good = [sim.run_protocol(rng) for _ in range(V4_TRIALS)]
    noc = [sim.run_protocol(rng, skip_out_correction=True) for _ in range(V4_TRIALS)]
    noq = [sim.run_protocol(rng, charge_mode='none') for _ in range(V4_TRIALS)]
    noc_n = [r for r in noc if r['n_correction_gates'] > 0]
    noq_n = [r for r in noq if r['n_charges'] > 0]
    rows.append(dict(N=N, L='x'.join(map(str, L)), 正しい手順_F最小=min(r['fidelity'] for r in good),
                     補正なし_該当試行=len(noc_n), 補正なし_F最大=max([r['fidelity'] for r in noc_n], default=float('nan')),
                     補正なし_F平均=np.mean([r['fidelity'] for r in noc_n]) if noc_n else float('nan'),
                     電荷放置_該当試行=len(noq_n), 電荷放置_F最大=max([r['fidelity'] for r in noq_n], default=float('nan'))))
V4 = pd.DataFrame(rows)
display(V4)
ok = (V4['正しい手順_F最小'] > 1 - 1e-9).all() and (V4['補正なし_F平均'] < 0.99).all() and (V4['電荷放置_F最大'] < 0.99).all() \
     and (V4['補正なし_該当試行'] > 0).all() and (V4['電荷放置_該当試行'] > 0).all()
record('V4 負の対照（補正を省くと忠実度が下がる）', ok,
       f"補正なしの平均 {V4['補正なし_F平均'].max():.3f} 以下、電荷放置の最大 {V4['電荷放置_F最大'].max():.3f}")
