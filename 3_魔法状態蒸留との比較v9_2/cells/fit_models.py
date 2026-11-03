# Exact multinomial likelihood for zero/half/full infidelity categories.
import analysis_v9_2 as a92
FITS, FIT_DIAGNOSTICS = a92.fit_models(main, quiet, SCENARIOS, n_boot=N_BOOT, seed=SEED+1, window_dmin=W_DMIN)
a92.write_diagnostics(f'{RESULTS}/fit_diagnostics{OUT_SUFFIX}.json', FIT_DIAGNOSTICS)
VARIANTS = ('main', 'altW', 'W5')
def eps_K_model(s, d, p, w='noisy', params=None, variant='main'):
    return a92.model_epsilon(FITS, s, d, p, w, params, variant)
fit_rows = []
for s in SCENARIOS:
    for d in (3,5,7,9):
        for p in P_EVAL:
            for window in ('noisy','quiet'):
                draws = [eps_K_model(s,d,p,window,bt) for bt in FITS[s]['boot']]
                fit_rows.append(dict(scenario=s,d=d,p=p,window=window,
                       eps_model=eps_K_model(s,d,p,window),model_025=np.quantile(draws,.025),
                       model_975=np.quantile(draws,.975),n_boot=N_BOOT,
                       model_fit_domain=(d>=W_DMIN if window=='noisy' else True)))
FIT_TABLE = pd.DataFrame(fit_rows)
FIT_TABLE.to_csv(f'{RESULTS}/model_predictions{OUT_SUFFIX}.csv',index=False)
print('multinomial fits:',len(FIT_DIAGNOSTICS),'successful; boundary fits:',sum(x['boundary'] for x in FIT_DIAGNOSTICS))
FIT_TABLE
