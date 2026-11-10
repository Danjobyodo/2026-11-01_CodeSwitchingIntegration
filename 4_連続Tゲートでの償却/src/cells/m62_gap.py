# 間の FSC ラウンドを短くしたときの誤りの変化：eps_cycle(gap) / eps_cycle(gap = d)
def gap_effect(pc):
    rows = []
    if 'eps_cycle' not in pc.columns:
        return pd.DataFrame(rows)
    for (scen, p, d), grp in pc.groupby(['scenario', 'p', 'd']):
        full = grp[(grp.gap == d) & grp.eps_cycle.notna()]
        if full.empty:
            continue
        f = full.iloc[0]
        for r in grp[(grp.gap != d) & grp.eps_cycle.notna()].itertuples():
            ratio = r.eps_cycle / f.eps_cycle if f.eps_cycle > 0 else np.nan
            se = abs(ratio) * np.sqrt((r.se_cycle / r.eps_cycle) ** 2 + (f.se_cycle / f.eps_cycle) ** 2) if f.eps_cycle > 0 and r.eps_cycle > 0 else np.nan
            a = COST[(COST.d == d)]
            rows.append(dict(scenario=scen, p=p, d=d, gap=r.gap, eps_cycle_gap=r.eps_cycle, eps_cycle_full=f.eps_cycle,
                             error_ratio=ratio, se_error_ratio=se,
                             volume_ratio=float(a[a.gap == r.gap].V_cycle.iloc[0] / a[a.gap == d].V_cycle.iloc[0]) if (a.gap == r.gap).any() else np.nan))
    return pd.DataFrame(rows)


GAP = gap_effect(PC)
GAP.to_csv(f'{OUT_DIR}/study4_gap_effect.csv', index=False)
GAP
