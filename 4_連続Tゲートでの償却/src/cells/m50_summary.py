# ==================================================================================================
# 集計：点ごとの不忠実度
#   1 ショットの不忠実度は 0, 1/2, 1 のどれか。eps = (n_one + n_half / 2) / N。
#   標準誤差は多項分布の分散から。区間は n_one と n_half のそれぞれの Clopper–Pearson 区間を Bonferroni で
#   合成したもの（ショット数が固定なので有効。保守的）。
# ==================================================================================================
def cp_interval(k, n, alpha):
    lo = 0.0 if k == 0 else _st.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else _st.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return lo, hi


def summarize_mc(mc):
    g = mc.groupby(['scenario', 'window', 'p', 'd', 'K', 'gap'], as_index=False).agg(
        shots=('shots', 'sum'), n_half=('n_half', 'sum'), n_one=('n_one', 'sum'), seconds=('seconds', 'sum'))
    g['eps'] = (g.n_one + g.n_half / 2) / g.shots
    p1, ph = g.n_one / g.shots, g.n_half / g.shots
    g['se'] = np.sqrt(np.maximum(p1 + ph / 4 - g.eps ** 2, 0) / g.shots)
    a = (1 - CONFIDENCE) / 2                      # Bonferroni：2 成分に半分ずつ
    lo, hi = [], []
    for r in g.itertuples():
        l1, h1 = cp_interval(r.n_one, r.shots, a)
        l2, h2 = cp_interval(r.n_half, r.shots, a)
        lo.append(l1 + l2 / 2); hi.append(h1 + h2 / 2)
    g['eps_lo'], g['eps_hi'] = lo, hi
    return g


def load_mc():
    path = f'{OUT_DIR}/study4_mc.csv'
    if os.path.exists(path):
        print('読み込み：', path)
        return pd.read_csv(path), 'this_run'
    print('OUT_DIR に CSV が無いので、ノートに埋め込んだ試行データ（results_pilot）を使います')
    return pd.read_csv(io.StringIO(EMBED_PILOT_MC)), 'embedded_pilot'


MC, MC_SOURCE = load_mc()
SUM = summarize_mc(MC)
SUM.to_csv(f'{OUT_DIR}/study4_summary.csv', index=False)
print('合計ショット数：', int(MC.shots.sum()))
SUM[SUM.window == 'noisy'][['scenario', 'p', 'd', 'K', 'gap', 'shots', 'n_half', 'n_one', 'eps', 'se', 'eps_lo', 'eps_hi']]
