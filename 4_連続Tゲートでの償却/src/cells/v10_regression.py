# V1：K = 1 の SeqExperiment は研究 3 の D4Experiment と同じ回路・同じ雑音位置・同じ復号器で、
#     同じ seed なら 1 ショットごとに同じ不忠実度を返す（研究 3 の検証と本番データをそのまま引き継げる根拠）
for d, p, f, n in V1_CASES:
    a = D4Experiment(d, d, d, d, NoiseModel(p, p_idle=f * p))
    b = SeqExperiment(d, d, d, d, d, 1, NoiseModel(p, p_idle=f * p))
    same_circuit = (a.comp.n_loc == b.comp.n_loc and np.array_equal(a.comp.loc_p, b.comp.loc_p)
                    and [len(x['moms']) for x in a.comp.blocks] == [len(x['moms']) for x in b.comp.blocks])
    ia, _ = a.run(n, np.random.default_rng(SEED)); ib, _ = b.run(n, np.random.default_rng(SEED))
    record(f'V1 d={d}, p={p:g}, idle={f:g}: K=1 が研究 3 と 1 ショットごとに一致', same_circuit and np.array_equal(ia, ib),
           f'{n} ショット、失敗 {int((ia > 0).sum())} 件、雑音位置 {a.comp.n_loc}')
