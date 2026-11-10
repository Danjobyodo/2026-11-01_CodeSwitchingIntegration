# V5：その他の整合性
# (a) 回路から数えた体積・時間が研究 3 の式（体積 632 d^3 + 454 d^2 + 8 d - 14、時間 62 d + 21）と一致
ok = all(seq_counts(d, 1)['volume_total'] == 632 * d ** 3 + 454 * d ** 2 + 8 * d - 14 and seq_counts(d, 1)['time_steps'] == 62 * d + 21
         for d in (3, 5, 7))
record('V5a K=1 の体積・時間が研究 3 の式と一致（d=3,5,7）', ok)
# (b) K サイクルの体積は K について線形（1 サイクルあたりの体積が一定）
c = [seq_counts(5, K, Rgap=3)['volume_total'] for K in (1, 2, 3, 4)]
record('V5b 体積が K について線形', len({c[i + 1] - c[i] for i in range(3)}) == 1, f'1 サイクルあたり {c[1] - c[0]}')
# (c) 同じ seed で同じ結果（再現性）
d, K, p, n = V5_CASE
ex = SeqExperiment(d, d, d, 1, d, K, NoiseModel(p, p_idle=0.0))
i1, _ = ex.run(n, np.random.default_rng(SEED)); i2, _ = ex.run(n, np.random.default_rng(SEED))
record('V5c 同じ seed で同じ結果', bool(np.array_equal(i1, i2)), f'd={d}, K={K}, {n} ショット')
# (d) 検出器と論理観測量が雑音なしの回路で決定的（stim が誤りモデルを作れる）＝復号器の定義が K サイクルで整合
ok = True
for d, K in [(3, 2), (3, 3), (5, 2)]:
    ex = SeqExperiment(d, d, d, 1, d, K, NoiseModel(1e-3))
    ok &= all(ch.stim_circuit.num_detectors == len(ch.dets) and ch.stim_circuit.num_observables == 1 for ch in ex.charges)
record('V5d 電荷復号器の検出器・観測量が決定的（d=3,5, K=2,3）', ok)
# (e) 1 サイクルの論理安定化子の線形係数は全て奇数（S 型）で、proxy に残る Z（a_i = 2）は無い
vals = {d: sorted(set(D4SwitchingCircuit(d, 1, 1, 1).Delta_a.values())) for d in (2, 3, 4, 5, 7)}
record('V5e 1 サイクルの Delta の線形係数に a_i = 2 が無い（proxy は X^t だけ）', all(2 not in v for v in vals.values()), str(vals))
