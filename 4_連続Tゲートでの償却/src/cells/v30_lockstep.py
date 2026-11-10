# V3：真の非 Clifford 回路との照合（研究 3 の N3b と同じ方法を K >= 2 に適用）。
#     同じ誤り・同じ測定結果を、Pauli proxy 回路（stim）と、CCZ・CS・T^dagger をそのまま作用させる厳密な
#     疎状態ベクトル（TrueSim）に与える。全ての測定で「proxy で決定的 ⇔ 厳密な確率 1」「proxy でランダム ⇔
#     厳密な確率 1/2」、最後に論理安定化子の期待値 <H> が一致することを確かめる。
#     フラックス復号器の補正、switch-out の復号と物理的な CZ の層、Pauli フレームを含む本番と同じ処理を通す。
#     S0 は研究 3 と同じく理想出力＋ランダムな Pauli 誤りで置き換える。
rng = np.random.default_rng(SEED)
rows = []
for (L, K, Rin, Rgap, p, ntr) in V3_CASES:
    ex = SeqExperiment(L, 1, Rin, Rgap, 1, K, NoiseModel(p))
    bad = nm = nr = nco = ncz = 0
    herr, infs = 0.0, []
    for tr in range(ntr):
        r = lockstep_full(L, Rin, 1, NoiseModel(p), rng, ex=ex)
        bad += not r['agree']; nm += r['n_meas']; nr += r['n_random']; nco += r['n_corr']; ncz += r['so_cz']
        herr = max(herr, abs(r['H_true'] - r['H_proxy'])); infs.append(r['infidelity'])
    rows.append(dict(L=L, K=K, Rin=Rin, Rgap=Rgap, p=p, runs=ntr, mismatched_runs=bad, measurements=nm, random=nr,
                     flux_corrections=nco, switch_out_cz=ncz, max_H_diff=herr, infidelity_values=sorted(set(infs))))
    record(f'V3 L={L}, K={K}, Rin={Rin}, Rgap={Rgap}, p={p:g}: proxy = 真の非 Clifford 回路（{ntr} 軌道）', bad == 0,
           f'測定 {nm} 個（ランダム {nr}）、補正 {nco}、switch-out の CZ {ncz}、|<H>| の差の最大 {herr:.1e}')
pd.DataFrame(rows)
