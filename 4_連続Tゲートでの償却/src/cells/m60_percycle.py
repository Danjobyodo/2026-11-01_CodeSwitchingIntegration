# ==================================================================================================
# 1 サイクルあたりの誤り
#   eps_cycle = (eps(K=K_hi) - eps(K=1)) / (K_hi - 1)   … S0 と最後の評価の寄与は差で消える
#   m         = eps_cycle / eps(K=1)                     … 1 に近ければ「誤りはサイクル数に比例し、連続実行で
#                                                           1 個あたりの誤りは減りも増えもしない」
#   K_hi は奇数の最大値を使う（K が奇数の出力は T 型の状態で、論理 X・Y 誤りに対する感度が K=1 と同じ。
#   偶数の K は感度が違うので参考値として別に示す）。区間は正規近似（独立な標本の差）。
# ==================================================================================================
def per_cycle(sumdf, window='noisy'):
    z = _st.norm.ppf(1 - (1 - CONFIDENCE) / 2)
    s = sumdf[sumdf.window == window]
    rows = []
    for (scen, p, d), grp in s.groupby(['scenario', 'p', 'd']):
        base = grp[grp.K == 1]
        if base.empty:
            continue
        b = base.iloc[0]
        ref = REF3[(REF3.scenario == scen) & np.isclose(REF3.p, p) & (REF3.d == d)]
        for gap, gg in grp[grp.K > 1].groupby('gap'):
            row = dict(scenario=scen, p=p, d=d, gap=int(gap), eps1=b.eps, se1=b.se, shots1=int(b.shots),
                       eps1_study3=float(ref.eps.iloc[0]) if len(ref) else np.nan)
            for K in sorted(gg.K):
                r = gg[gg.K == K].iloc[0]
                row[f'eps{K}'], row[f'se{K}'] = r.eps, r.se
            odd = [K for K in sorted(gg.K) if K % 2 == 1]
            if odd:
                Kh = odd[-1]
                r = gg[gg.K == Kh].iloc[0]
                ec = (r.eps - b.eps) / (Kh - 1)
                sec = np.sqrt(r.se ** 2 + b.se ** 2) / (Kh - 1)
                m = ec / b.eps if b.eps > 0 else np.nan
                # デルタ法：m = (eps_K/eps_1 - 1)/(K-1)
                sem = (np.sqrt((r.se / b.eps) ** 2 + (r.eps * b.se / b.eps ** 2) ** 2) / (Kh - 1)) if b.eps > 0 else np.nan
                row.update(K_hi=Kh, eps_cycle=ec, se_cycle=sec, eps_cycle_lo=ec - z * sec, eps_cycle_hi=ec + z * sec,
                           m=m, se_m=sem, m_lo=m - z * sem, m_hi=m + z * sem)
            rows.append(row)
    return pd.DataFrame(rows)


PC = per_cycle(SUM)
PC.to_csv(f'{OUT_DIR}/study4_per_cycle.csv', index=False)
_cols = [c for c in ['scenario', 'p', 'd', 'gap', 'shots1', 'eps1', 'eps1_study3', 'eps2', 'eps3', 'eps_cycle', 'se_cycle', 'm', 'm_lo', 'm_hi'] if c in PC.columns]
PC[_cols]
