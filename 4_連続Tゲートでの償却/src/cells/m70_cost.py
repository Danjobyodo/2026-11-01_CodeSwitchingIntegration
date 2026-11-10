# ==================================================================================================
# 費用の比較（T ゲート 1 個あたりの時空間体積：連続実行の code switching ÷ 15-to-1 蒸留）
#
# 研究 3 の比（1 回の魔法状態準備の体積 ÷ 蒸留工場の体積）を出発点に、連続実行による変化を掛ける：
#     比_連続 = 比_研究3 × alpha(d, gap) ÷ (1 + c)
#   alpha : 償却係数（上のセル）。d は研究 3 と同じサイズを使う。
#           これは「1 サイクルあたりの誤りが研究 3 の 1 回の誤り以下（m <= 1）」のときに成り立つ。
#           m > 1 なら必要なサイズは研究 3 以上になり、比はこれより大きくなる（＝この表は code switching に有利な側）。
#   c     : 蒸留側で魔法状態を消費する格子手術の体積 ÷ 工場の体積（CONSUME_OVERHEAD）。研究 3 は c = 0。
# 研究 3 の列の意味：status = data_certified ならデータで保証された比、それ以外は「データで棄却されない最小の
# サイズ」での比（＝体積の下限。保証ではない）。
# ==================================================================================================
def alpha_of(d, gap):
    rg = gap_rounds(gap, d)
    hit = COST[(COST.d == d) & (COST.gap == rg)]
    if len(hit):
        return float(hit.alpha.iloc[0])
    c1, c2 = seq_counts(d, 1, n_pre_u=N_PRE_U), seq_counts(d, 2, Rgap=rg, n_pre_u=N_PRE_U)
    return (c2['volume_total'] - c1['volume_total']) / c1['volume_total']


def amortized_table(targets, gaps, overheads):
    rows = []
    for r in STUDY3[STUDY3.target.isin(targets)].itertuples():
        d = int(r.kobayashi_d_low)
        row = dict(scenario=r.scenario, p=r.p, target=r.target, study3_status=r.kobayashi_status, d=d,
                   d_simulated=d <= 9, ratio_study3=r.ratio_kobayashi_low_over_litinski)
        for gap in gaps:
            for c in overheads:
                row[f'ratio_seq_gap{gap}_c{c:g}'] = r.ratio_kobayashi_low_over_litinski * alpha_of(d, gap) / (1 + c)
        # 損益分岐に必要な消費の体積（工場の体積に対する比）：比_研究3 × alpha - 1
        row['c_needed_gap_d'] = r.ratio_kobayashi_low_over_litinski * alpha_of(d, 'd') - 1
        row['c_needed_gap_1'] = r.ratio_kobayashi_low_over_litinski * alpha_of(d, 1) - 1
        rows.append(row)
    return pd.DataFrame(rows)


AMORT = amortized_table(TARGETS, ['d', 1], CONSUME_OVERHEAD)
AMORT.to_csv(f'{OUT_DIR}/study4_amortized_cost.csv', index=False)
_t = AMORT[AMORT.target == TARGETS[0]]
print(f'要求 {TARGETS[0]:g}：比_連続（c = 0）の最小値  gap = d : {_t["ratio_seq_gapd_c0"].min():.2f}   gap = 1 : {_t["ratio_seq_gap1_c0"].min():.2f}'
      f'   （研究 3 の比の最小値 {_t.ratio_study3.min():.2f}）')
AMORT[AMORT.target == TARGETS[0]].round(3)
