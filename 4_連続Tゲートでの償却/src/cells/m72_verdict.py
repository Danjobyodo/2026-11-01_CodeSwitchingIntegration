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
        full = PC[(PC.gap == PC.d) & PC.m.notna()]
        out.append('[誤り] m = eps_cycle / eps(K=1)（gap = d）： ' + '、'.join(
            f'{r.scenario},p={r.p:g},d={r.d}: {r.m:.2f} [{r.m_lo:.2f}, {r.m_hi:.2f}]' for r in full.itertuples()))
        if len(full) > 1:                       # 逆分散重みの平均（点の間で m が共通と仮定した参考値）と一様性の chi^2
            w = 1 / full.se_m ** 2
            mp = float((w * full.m).sum() / w.sum())
            out.append(f'      全点の重み付き平均 m = {mp:.3f} ± {float(w.sum() ** -0.5):.3f}'
                       f'（chi^2 = {float((((full.m - mp) / full.se_m) ** 2).sum()):.1f}, 自由度 {len(full) - 1}）')
        lowm = full[full.m_hi < 1]
        out.append(f'      m が 1 より有意に小さい点（連続実行で 1 個あたりの誤りが減る点）：{len(lowm)} / {len(full)}')
    if len(GAP):
        out.append('[間のラウンド] eps_cycle(gap) / eps_cycle(gap=d)： ' + '、'.join(
            f'{r.scenario},p={r.p:g},d={r.d},gap={r.gap}: {r.error_ratio:.2f}±{r.se_error_ratio:.2f}（体積 {r.volume_ratio:.2f} 倍）' for r in GAP.itertuples()))
    if len(GAP) > 1:
        w = 1 / GAP.se_error_ratio ** 2
        rp = float((w * GAP.error_ratio).sum() / w.sum())
        out.append(f'      全点の重み付き平均 = {rp:.3f} ± {float(w.sum() ** -0.5):.3f}'
                   f'（chi^2 = {float((((GAP.error_ratio - rp) / GAP.se_error_ratio) ** 2).sum()):.1f}, 自由度 {len(GAP) - 1}）')
    out.append('[注意] データの出所：' + ('このノートの実行結果' if MC_SOURCE == 'this_run' else '埋め込みの試行データ') +
               f'（合計 {int(MC.shots.sum())} ショット）。費用の表は研究 3 の本番データ（554 万ショット）の判定に償却係数を掛けたもの。')
    return '\n'.join(out)


VERDICT = verdict()
open(f'{OUT_DIR}/study4_verdict.txt', 'w').write(VERDICT + '\n')
print(VERDICT)
