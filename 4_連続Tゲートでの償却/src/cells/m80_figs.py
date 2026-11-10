# ==================================================================================================
# 図（PNG を OUT_DIR に保存）。図の中の文字は英語（Colab に日本語フォントが無いため）。
# ==================================================================================================
_C = {'d': '#2a78d6', 'short': '#eb6834', 'ref': '#52514e'}
plt.rcParams.update({'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb', 'axes.edgecolor': '#c3c2b7',
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': '#e6e5e0',
                     'grid.linewidth': 0.6, 'font.size': 9, 'axes.titlesize': 9.5, 'legend.frameon': False})


def fig_eps_vs_K(sumdf):
    s = sumdf[sumdf.window == 'noisy']
    keys = sorted({(r.scenario, r.p, r.d) for r in s.itertuples()}, key=lambda k: (k[0], -k[1], k[2]))
    if not keys:
        return
    ncol = min(4, len(keys)); nrow = int(np.ceil(len(keys) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.1 * ncol, 2.7 * nrow), squeeze=False)
    for ax in axes.ravel()[len(keys):]:
        ax.axis('off')
    for ax, (scen, p, d) in zip(axes.ravel(), keys):
        g = s[(s.scenario == scen) & np.isclose(s.p, p) & (s.d == d)]
        b = g[g.K == 1]
        kmax = int(g.K.max())
        if len(b):
            ax.plot([1, kmax], [b.eps.iloc[0], kmax * b.eps.iloc[0]], color=_C['ref'], lw=1, ls=':', label='K x eps(K=1)')
        for gap in sorted(g[g.K > 1].gap.unique(), reverse=True):
            gg = pd.concat([b, g[(g.K > 1) & (g.gap == gap)]]).sort_values('K')
            full = gap == d
            ax.errorbar(gg.K + (0 if full else 0.06), gg.eps, yerr=[gg.eps - gg.eps_lo, gg.eps_hi - gg.eps], lw=2, capsize=2,
                        color=_C['d'] if full else _C['short'], marker='o' if full else 's', ms=5,
                        label=f'gap = {int(gap)} rounds' + (' (= d)' if full else ''))
        ax.set_title(f'scenario {scen}, p = {p:g}, d = {d}')
        ax.set_xticks(range(1, kmax + 1)); ax.set_ylim(bottom=0)
        ax.set_xlabel('number of consecutive cycles K'); ax.set_ylabel('output infidelity')
        ax.legend(fontsize=7.5, loc='upper left')
    fig.tight_layout()
    fig.savefig(f'{OUT_DIR}/fig_eps_vs_K.png', dpi=200)
    plt.show()


def fig_ratio(amort, target):
    t = amort[amort.target == target].sort_values(['scenario', 'p']).reset_index(drop=True)
    if t.empty:
        return
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    y = np.arange(len(t))
    ax.axvline(1, color='#0b0b0b', lw=1)
    ax.scatter(t.ratio_study3, y, color=_C['ref'], marker='D', s=36, zorder=3, label='single preparation (study 3)')
    ax.scatter(t['ratio_seq_gapd_c0'], y, color=_C['d'], marker='o', s=40, zorder=3, label='consecutive, gap = d')
    ax.scatter(t['ratio_seq_gap1_c0'], y, color=_C['short'], marker='s', s=36, zorder=3, label='consecutive, gap = 1 (if no extra error)')
    ax.hlines(y, t['ratio_seq_gap1_c0'], t.ratio_study3, color='#c3c2b7', lw=1, zorder=1)
    ax.set_yticks(y); ax.set_yticklabels([f'{r.scenario}, p = {r.p:g}, d = {r.d}' + ('' if r.d_simulated else '*') for r in t.itertuples()])
    ax.set_xscale('log'); ax.invert_yaxis()
    ax.set_xlabel('volume per T gate: code switching / 15-to-1 distillation   (< 1: code switching cheaper)')
    ax.set_xlim(left=min(0.8, 0.9 * t['ratio_seq_gap1_c0'].min()))
    ax.set_title(f'target error per T gate = {target:g}   (* size not simulated: weak lower bound)', pad=26)
    ax.legend(fontsize=7.5, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=3, borderaxespad=0.2)
    fig.tight_layout()
    fig.savefig(f'{OUT_DIR}/fig_cost_ratio.png', dpi=200)
    plt.show()


fig_eps_vs_K(SUM)
fig_ratio(AMORT, TARGETS[0])
