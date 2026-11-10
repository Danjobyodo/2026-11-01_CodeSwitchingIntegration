# V2：雑音なしなら、K 回連続しても出力は理想状態 (T^dagger)^K |+> と一致する（不忠実度 0）。
#     switch-in の S^g の結果と switch-out の読み出しは毎回ランダムなので、Pauli フレームと論理安定化子の
#     K 依存（Delta -> K Delta）が正しくなければ 0 にならない。
for d in V2_D:
    worst, nshot = 0.0, 0
    for K in V2_K:
        for gap in (1, 2):
            inf, _ = SeqExperiment(d, 1, d, gap, 1, K, NoiseModel(0.0)).run(V2_SHOTS, np.random.default_rng(SEED + K))
            worst = max(worst, float(inf.max())); nshot += V2_SHOTS
    record(f'V2 d={d}: 雑音なしで不忠実度 0（K={V2_K}）', worst == 0.0, f'{nshot} ショット')
