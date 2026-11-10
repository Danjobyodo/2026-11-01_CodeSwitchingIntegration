# ==================================================================================================
# §5 損益分岐の見積もり：sqrt(T)（N=4）を 3 次元の code switching で作る vs. Clifford+T で合成する
#   注意：これは雑音のシミュレーションではない。3 次元の code switching の誤り率は分かっていない。
#        「合成の費用を予算とすると、3 次元の code switching は何ステップまで使ってよいか」を計算するだけである。
#   合成側   sqrt(T) 1 個の誤りを delta 以下にする。合成誤り delta/2、T ゲート n_T 個の誤りの合計 delta/2
#            n_T = T_COUNT_COEF * log2(2/delta) + T_COUNT_CONST、T 1 個の要求誤り = delta / (2 n_T)
#            T 1 個の体積 = 研究 3 の表の 15-to-1 蒸留の体積（要求誤りについて log-log で内挿）
#   switching 側  量子ビット数 = ANCILLA_FACTOR × データ量子ビット数（§3 と同じ数え方）
#   出力     許されるステップ数 = 合成の体積 ÷ switching の量子ビット数。
#            参考：2 次元の T の code switching（研究 3）は同じ d で 62 d + 21 ステップ
# ==================================================================================================
s3 = STUDY3[(STUDY3.scenario == BREAKEVEN_SCENARIO) & np.isclose(STUDY3.p, BREAKEVEN_P)].sort_values('target')
assert len(s3), '研究 3 の表に、指定した (シナリオ, p) がない'
lt, lv, lq = np.log10(s3.target.values), np.log10(s3.litinski_volume.values), s3.litinski_qubits.values
rows = []
for delta in BREAKEVEN_DELTAS:
    n_T = math.ceil(T_COUNT_COEF * math.log2(2 / delta) + T_COUNT_CONST)
    need = delta / (2 * n_T)
    if not (lt[0] - 1e-9 <= math.log10(need) <= lt[-1] + 1e-9):
        rows.append({'delta': delta, 'n_T': n_T, 'T_要求誤り': float(f'{need:.2e}'), '備考': '研究 3 の表（要求 1e-10〜1e-4）の範囲外'}); continue
    vol_T = 10 ** float(np.interp(math.log10(need), lt, lv))            # 表の点の間は log-log で内挿
    fq = float(np.interp(math.log10(need), lt, lq))
    budget = n_T * vol_T
    for L in BREAKEVEN_L:
        q_kuhn = ANCILLA_FACTOR * Lattice(4, (L, L, L)).qubit_counts()['total']
        q_cubic = ANCILLA_FACTOR * 12 * L ** 3
        t2d = 62 * L + 21
        rows.append({'delta': delta, 'n_T': n_T, 'T_要求誤り': float(f'{need:.2e}'), 'T_1個の体積': float(f'{vol_T:.3e}'),
                     '合成の体積': float(f'{budget:.3e}'), '蒸留工場の量子ビット': int(fq), 'L': L,
                     'switching_量子ビット': int(q_kuhn), '量子ビットの比': round(q_kuhn / fq, 1),
                     '許されるステップ数': int(budget / q_kuhn), '参考_2次元のTのステップ': t2d,
                     '許される倍率': round(budget / q_kuhn / t2d, 2),
                     '許される倍率_立方格子': round(budget / q_cubic / t2d, 2)})
BE = pd.DataFrame(rows)
BE.to_csv(os.path.join(OUT_DIR, 'study5_breakeven.csv'), index=False)
display(BE)
print('読み方：「許される倍率」= 許されるステップ数 ÷ (62 L + 21)。これが 1 より十分大きい L で、3 次元の code switching が')
print('        誤り delta に届くなら、体積で得になる。届くかどうか（3 次元の符号の閾値と必要な L）は、この研究では分からない。')
print('        「立方格子」の列は、量子ビット数を 12 L^3（辺 3 L^3 本 × 4 色。Kuhn 分割の斜めの辺が無い場合）とした参考値。')
