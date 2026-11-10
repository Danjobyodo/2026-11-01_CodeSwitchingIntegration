# ==================================================================================================
# 判定の要約（文章）。数値は上の表から機械的に作る。
# ==================================================================================================
def verdict():
    out = []
    t = AMORT[AMORT.target == TARGETS[0]]
    out.append(f'[費用] 要求 {TARGETS[0]:g} の {len(t)} 条件：連続実行の比（c=0）は gap=d で {t["ratio_seq_gapd_c0"].min():.2f}〜{t["ratio_seq_gapd_c0"].max():.2f}、'
               f'gap=1 で {t["ratio_seq_gap1_c0"].min():.2f}〜{t["ratio_seq_gap1_c0"].max():.2f}。1 を下回る条件は '
               f'gap=d で {int((t["ratio_seq_gapd_c0"] < 1).sum())} 個、gap=1 で {int((t["ratio_seq_gap1_c0"] < 1).sum())} 個。')
    if len(PC) and 'm' in PC.columns:
        full = PC[PC.gap == PC.d]
        out.append('[誤り] m = eps_cycle / eps(K=1)（gap = d）： ' + '、'.join(
            f'{r.scenario},p={r.p:g},d={r.d}: {r.m:.2f} [{r.m_lo:.2f}, {r.m_hi:.2f}]' for r in full.itertuples()))
        lowm = full[full.m_hi < 1]
        out.append(f'      m が 1 より有意に小さい点（連続実行で 1 個あたりの誤りが減る点）：{len(lowm)} / {len(full)}')
    if len(GAP):
        out.append('[間のラウンド] eps_cycle(gap) / eps_cycle(gap=d)： ' + '、'.join(
            f'{r.scenario},p={r.p:g},d={r.d},gap={r.gap}: {r.error_ratio:.2f}±{r.se_error_ratio:.2f}（体積 {r.volume_ratio:.2f} 倍）' for r in GAP.itertuples()))
    out.append('[注意] データの出所：' + ('このノートの実行結果' if MC_SOURCE == 'this_run' else '埋め込みの試行データ') +
               f'（合計 {int(MC.shots.sum())} ショット）。費用の表は研究 3 の本番データ（554 万ショット）の判定に償却係数を掛けたもの。')
    return '\n'.join(out)


VERDICT = verdict()
open(f'{OUT_DIR}/study4_verdict.txt', 'w').write(VERDICT + '\n')
print(VERDICT)
