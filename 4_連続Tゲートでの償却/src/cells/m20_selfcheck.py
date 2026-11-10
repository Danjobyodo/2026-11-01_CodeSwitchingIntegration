# ==================================================================================================
# 自己検査（1〜2 分）。詳しい検証は 研究4_validation.ipynb。
# ==================================================================================================
def selfcheck():
    ok = True
    # (1) K = 1 は研究 3 の D4Experiment と 1 ショットごとに同じ結果（同じ seed）
    a = D4Experiment(3, 3, 3, 3, NoiseModel(2e-3, p_idle=0.0))
    b = SeqExperiment(3, 3, 3, 3, 3, 1, NoiseModel(2e-3, p_idle=0.0))
    ia, _ = a.run(300, np.random.default_rng(5)); ib, _ = b.run(300, np.random.default_rng(5))
    r = bool(np.array_equal(ia, ib)); ok &= r
    print('[%s] K=1 が研究 3 の回路・復号器と 1 ショットごとに一致（300 ショット、失敗 %d 件）' % ('PASS' if r else 'FAIL', int((ia > 0).sum())))
    # (2) 雑音なしなら K 回連続でも不忠実度 0
    worst = 0.0
    for d, K in [(2, 2), (3, 2), (3, 3), (4, 4)]:
        inf, _ = SeqExperiment(d, 1, d, 1, 1, K, NoiseModel(0.0)).run(10, np.random.default_rng(K))
        worst = max(worst, float(inf.max()))
    r = worst == 0.0; ok &= r
    print('[%s] 雑音なしで不忠実度 0（d=2..4, K=2..4）' % ('PASS' if r else 'FAIL'))
    # (3) 真の非 Clifford 回路（厳密な疎状態ベクトル）との照合：L=2, K=2 の全測定と最後の <H>
    rng = np.random.default_rng(3)
    ex = SeqExperiment(2, 1, 1, 1, 1, 2, NoiseModel(0.02))
    bad = nm = 0
    for _ in range(3):
        res = lockstep_full(2, 1, 1, NoiseModel(0.02), rng, ex=ex)
        bad += not res['agree']; nm += res['n_meas']
    r = bad == 0; ok &= r
    print('[%s] L=2, K=2：Pauli proxy と真の非 Clifford 回路が一致（3 軌道、測定 %d 個）' % ('PASS' if r else 'FAIL', nm))
    assert ok, '自己検査に失敗しました'


if RUN_SELFCHECK and RUN_MODE != 'analysis_only':
    selfcheck()
