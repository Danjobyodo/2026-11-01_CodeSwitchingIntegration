# v13: the two figures are drawn at the end, from the CSVs written above (figures_v13.py; no computation there).
# model_curves.csv holds the curves of the figures: the central fit on a grid of p ('vs_p', sizes simulated)
# and on a grid of d ('vs_d', with the space-time volume of that size).
import figures_v13 as figs
curve_rows = []
for s in SCENARIOS:
    for w_ in ('noisy', 'quiet'):
        for d in (3, 5, 7, 9):
            for p in np.logspace(-4.2, -2.9, 40):
                curve_rows.append(dict(curve='vs_p', scenario=s, window=w_, d=d, p=p, eps_model=eps_K_model(s, d, p, w_)))
        for p in P_EVAL:
            for d in range(3, 61, 2):
                curve_rows.append(dict(curve='vs_d', scenario=s, window=w_, d=d, p=p, eps_model=eps_K_model(s, d, p, w_)))
MODEL_CURVES = pd.DataFrame(curve_rows)
MODEL_CURVES['volume'] = [kobayashi_cost(d)['volume'] for d in MODEL_CURVES.d]
MODEL_CURVES['in_fit_domain'] = [model_allowed(w_, d) for w_, d in zip(MODEL_CURVES.window, MODEL_CURVES.d)]
MODEL_CURVES['d_extrapolated'] = [d > FITS[s]['d_max_data'] for s, d in zip(MODEL_CURVES.scenario, MODEL_CURVES.d)]
MODEL_CURVES['p_extrapolated'] = [p < FITS[s]['p_min_bulk'] for s, p in zip(MODEL_CURVES.scenario, MODEL_CURVES.p)]
MODEL_CURVES.to_csv(f'{RESULTS}/model_curves{OUT_SUFFIX}.csv', index=False)
for path in figs.make_all(RESULTS, FIGURES, OUT_SUFFIX, show=True):
    print('wrote', path)
