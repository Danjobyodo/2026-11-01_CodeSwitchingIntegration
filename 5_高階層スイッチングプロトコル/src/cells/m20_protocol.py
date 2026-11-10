# ==================================================================================================
# §2 code switching の厳密な実行（状態ベクトル）
#   手順  0. Pauli 符号（N-1 枚のトーリック符号を B_N で貼り合わせたもの）の |+> と、特別な色の |0...0>
#         1. switch-in ：特別な色の X 型安定化子 S^s_v（階層 N-1 の演算子）を全て測る。結果は ±1 の乱数
#         2. 結果 -1（電荷）の処理。方式 'fix_before_U'：その場で Z の弦で消す
#                                   方式 'frame'       ：消さずに進み、最後に Pauli フレームで消す
#         3. 論理ゲート U = W V
#         4. switch-out：特別な色を全ての辺で Z 測定し、結果に応じて C^(N-2)Z の補正をかける
#         5. 出力と R_N |+> の忠実度
#   表の列  U_phase     : 符号空間での U = diag(1, exp(i pi x)) の x（状態ベクトルから直接求めた値）
#           漏れ         : U が符号空間から状態を漏らす量（0 のはず）
#           F_min        : 全試行の忠実度の最小値（1 のはず）
#           F(+)         : 何もしない場合の値 |<+|R_N|+>|^2（比較用。これと区別できていることを確認する）
#           電荷 / 反転   : switch-in の結果 -1 の数、switch-out で反転を読んだ頂点の数（試行平均）
# ==================================================================================================
rng = np.random.default_rng(SEED)
rows, trials = [], []
for N, L in CASES['protocol']:
    lat = Lattice(N, L)
    D = Sector(lat).D
    if D > MAX_D:
        print(f'N={N}, L={L}: D={D} > MAX_D={MAX_D} なので飛ばす'); continue
    t0 = time.time()
    sim = StateSim(lat, max_D=MAX_D)
    M, leak, stab = sim.logical_matrix()
    uphase = float(np.angle(M[1, 1] / M[0, 0]) / np.pi)
    for mode in ('fix_before_U', 'frame'):
        res = [sim.run_protocol(rng, mode) for _ in range(N_TRIALS)]
        for i, r in enumerate(res):
            trials.append(dict(N=N, L='x'.join(map(str, L)), mode=mode, trial=i, **r))
        rows.append(dict(N=N, L='x'.join(map(str, L)), D=D, 方式=mode, 試行=N_TRIALS,
                         U_phase=round(uphase, 6), 期待値=1 / 2 ** (N - 1), 漏れ=float(f'{leak:.1e}'),
                         F_min=min(r['fidelity'] for r in res), F_plus=round(res[0]['fidelity_to_plus'], 4),
                         電荷=np.mean([r['n_charges'] for r in res]), 測定数=res[0]['n_measured'],
                         反転=np.mean([r['n_flux_out'] for r in res]),
                         補正ゲート=np.mean([r['n_correction_gates'] for r in res]),
                         P0_範囲=f"{min(r['prob0_min'] for r in res):.3f}〜{max(r['prob0_max'] for r in res):.3f}",
                         秒=round(time.time() - t0, 1)))
        print(rows[-1], flush=True)
    del sim
PROTO = pd.DataFrame(rows)
PROTO.to_csv(os.path.join(OUT_DIR, 'study5_protocol.csv'), index=False)
pd.DataFrame(trials).to_csv(os.path.join(OUT_DIR, 'study5_protocol_trials.csv'), index=False)
display(PROTO)
assert (PROTO['F_min'] > 1 - 1e-9).all() and (abs(PROTO['U_phase'] - PROTO['期待値']) < 1e-9).all()
print(f"§2：{len(PROTO) * N_TRIALS} 試行すべてで出力は R_N |+>（忠実度の最小値 {PROTO['F_min'].min():.12f}）")
