# ==================================================================================================
# 回路の規模と「償却係数」
#   V_single : 研究 3 と同じ 1 回の魔法状態準備（S0 + S1 + U + SO + S4）の時空間体積
#   V_cycle  : 連続実行で T ゲート 1 個が増えるごとに増える体積（S1 + U + SO + 間の FSC ラウンド）
#   alpha    : V_cycle / V_single（1 より小さいほど、連続実行で 1 個あたりが安くなる）
# ==================================================================================================
def cost_table(d_list, gaps):
    rows = []
    for d in d_list:
        c1 = seq_counts(d, 1, n_pre_u=N_PRE_U)
        for gap in gaps:
            rg = gap_rounds(gap, d)
            c2 = seq_counts(d, 2, Rgap=rg, n_pre_u=N_PRE_U)
            rows.append(dict(d=d, gap=rg, qubits=c1['qubits'], steps_single=c1['time_steps'], V_single=c1['volume_total'],
                             steps_cycle=c2['time_steps'] - c1['time_steps'], V_cycle=c2['volume_total'] - c1['volume_total']))
    df = pd.DataFrame(rows)
    df['alpha'] = df.V_cycle / df.V_single
    df['alpha_time'] = df.steps_cycle / df.steps_single
    return df


COST = cost_table([3, 5, 7, 9, 11], ['d', 'half', 1])
_c = seq_counts(5, 1)
assert _c['volume_total'] == 632 * 125 + 454 * 25 + 8 * 5 - 14 and _c['time_steps'] == 62 * 5 + 21    # 研究 3 の式と一致
COST.round(4)
