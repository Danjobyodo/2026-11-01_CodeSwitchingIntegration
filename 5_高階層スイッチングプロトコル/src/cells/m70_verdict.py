# ==================================================================================================
# §7 まとめ
# ==================================================================================================
lines = []
lines.append(f'RUN_MODE = {RUN_MODE}, SEED = {SEED}')
lines.append(f"§1 恒等式：{len(IDENT)} 個の格子（N = {IDENT.N.min()}〜{IDENT.N.max()}、最大 D = {IDENT.D.max()}）で全て合格 = {bool(IDENT['合格'].all())}。"
             f"論理ゲートは R_N（位相 pi/2^(N-1)）")
lines.append(f"§2 プロトコル：{len(PROTO)} 条件 × {N_TRIALS} 試行、忠実度の最小値 = {PROTO['F_min'].min():.12f}（N = {PROTO.N.min()}〜{PROTO.N.max()}）")
for N in sorted(RES.N.unique()):
    sub = RES[RES.N == N].iloc[-1]
    lines.append(f"§3 N={N}, L={sub.L}: qubits = {sub.qubits}, switch-in の検査の X の重み = {sub['Xの重み']}, "
                 f"修飾ゲート = {sub['修飾ゲート']} 個, X 誤りの広がり（上界）= {sub['X誤りの広がり_最大']}")
if '許される倍率' in BE.columns:
    for delta in sorted(BE.delta.unique(), reverse=True):
        sub = BE[(BE.delta == delta) & BE.L.notna()]
        if len(sub):
            lines.append(f"§5 delta = {delta:g}: n_T = {int(sub.n_T.iloc[0])}, 許される倍率（L = {list(sub.L.astype(int))}）= {list(sub['許される倍率'])}")
lines.append('注意：雑音は入れていない。§5 は損益分岐の条件で、code switching が有利という結論ではない。')
lines.append(f'所要時間 {time.time() - T_START:.0f} 秒')
open(os.path.join(OUT_DIR, 'study5_verdict.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
print('\n出力ファイル：', sorted(os.listdir(OUT_DIR)))
