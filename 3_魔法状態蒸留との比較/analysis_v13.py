"""v13 (statistics unchanged from v10; from v9.2): bounded-loss confidence intervals and categorical resource models.

Each independent shot has infidelity in {0, 1/2, 1}. No half-failure
Poisson likelihood is used. Models are descriptive, not confidence guarantees.
Library only (embedded in the notebooks; imported by the tests); it does not run anything by itself.
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize
from scipy.special import betaln, expit, logsumexp, xlogy

VERSION = "v13"
KEYS = ['window', 'scenario', 'd', 'p', 'p_idle', 'kappa0', 'kappa_in', 'kappa_out']


def aggregate_counts(mc):
    """Validate raw chunks before grouping; reject duplicate or inconsistent data."""
    required = KEYS + ['shots', 'sum_infidelity', 'n_fail', 'n_half', 'run_id', 'point_id', 'chunk_id', 'seed', 'R0', 'Rin', 'Rout']
    if not set(required) <= set(mc.columns):
        raise ValueError(f'missing columns: {sorted(set(required) - set(mc.columns))}')
    if mc.empty or mc[required].isna().any().any():
        raise ValueError('empty data or missing values')
    for col in ['shots', 'n_fail', 'n_half', 'chunk_id', 'seed']:
        v = mc[col].to_numpy(float)
        if not np.isfinite(v).all() or np.any(v != np.floor(v)) or np.any(v < 0):
            raise ValueError(f'{col} must contain nonnegative integers')
    if (mc.shots <= 0).any() or (mc.n_half > mc.n_fail).any() or (mc.n_fail > mc.shots).any():
        raise ValueError('invalid shot/category counts')
    if not mc.window.isin(['noisy','quiet']).all() or not mc.scenario.isin(['A','B']).all():
        raise ValueError('unknown scenario or window')
    for col in ['p','p_idle','d','kappa0','kappa_in','kappa_out']:
        if not np.isfinite(mc[col].to_numpy(float)).all():
            raise ValueError(f'nonfinite physical condition: {col}')
    if ((mc.p<=0)|(mc.p>1)|(mc.p_idle<0)|(mc.p_idle>1)|(mc.d<1)|(mc.d!=np.floor(mc.d))).any():
        raise ValueError('invalid physical probability or size')
    expected_idle = np.where(mc.scenario=='A',mc.p,0.)
    if not np.allclose(mc.p_idle,expected_idle,rtol=1e-12,atol=0):
        raise ValueError('scenario and idle rate disagree')
    for rounds,kappa in [('R0','kappa0'),('Rin','kappa_in'),('Rout','kappa_out')]:
        if (mc[kappa]<=0).any() or not np.array_equal(mc[rounds],np.maximum(1,np.ceil(mc[kappa]*mc.d))):
            raise ValueError('round counts differ from the declared d/kappa convention')
    if not np.allclose(mc.sum_infidelity, mc.n_fail - .5 * mc.n_half, rtol=0, atol=1e-9):
        raise ValueError('sum_infidelity disagrees with category counts')
    if mc.duplicated(['run_id', 'point_id', 'chunk_id']).any():
        raise ValueError('duplicate chunk identity')
    # Re-running a chunk under a new run_id does not create independent samples.
    if mc.duplicated(KEYS + ['seed']).any():
        raise ValueError('reused random seed for the same physical point')
    g = mc.groupby(KEYS, dropna=False).agg(shots=('shots', 'sum'), s=('sum_infidelity', 'sum'),
          n_fail=('n_fail', 'sum'), n_half=('n_half', 'sum')).reset_index()
    g['n_one'] = g.n_fail - g.n_half
    g['n_zero'] = g.shots - g.n_fail
    g['eps'] = g.s / g.shots
    g['stderr'] = np.sqrt(np.maximum((g.n_one + .25*g.n_half)/g.shots-g.eps**2, 0)/g.shots)
    return g


def counts(df):
    """Columns follow the order zero, half, one."""
    return df[['n_zero', 'n_half', 'n_one']].to_numpy(dtype=np.int64)


def bounded_mean_ci(row, cl=.95, family_size=1):
    """Fixed-sample Chernoff/KL interval for independent losses in [0,1].

    Convexity gives E exp(t X) <= 1-mu+mu exp(t). Invert the two
    Chernoff tails with alpha/(2*family_size) per tail. Thus Bonferroni
    covers the declared finite family simultaneously, without assuming that
    half and full errors are independent events. Not an anytime interval.
    """
    n = int(row['shots'])
    mean = float(row['s']) / n if n > 0 else np.nan
    if n <= 0 or n != row['shots'] or not 0 <= mean <= 1 or not 0 < cl < 1 or int(family_size) != family_size or family_size < 1:
        raise ValueError('invalid interval arguments')
    threshold = np.log(2*family_size/(1-cl))/n
    def kl(p):
        return float(xlogy(mean, mean)-xlogy(mean,p)
                     +xlogy(1-mean,1-mean)-xlogy(1-mean,1-p))
    if mean == 0:
        return 0., float(-np.expm1(-threshold))
    if mean == 1:
        return float(np.exp(-threshold)), 1.
    # brentq's absolute tolerance matters for rare logical error rates.
    lo = brentq(lambda p: kl(p)-threshold, np.nextafter(0., 1.), mean, xtol=1e-15)
    hi = brentq(lambda p: kl(p)-threshold, mean, np.nextafter(1., 0.), xtol=1e-15)
    return float(lo), float(hi)


def anytime_mean_cs(row, cl=.95, family_size=1):
    """Beta-mixture confidence sequence for bounded [0,1] losses.

    For each q, (q/mu)^X ((1-q)/(1-mu))^(1-X) has conditional
    expectation <=1 under mean mu, by convexity in X. Mixing over a
    Beta(1/2,1/2) q preserves the nonnegative supermartingale property.
    Ville + Bonferroni gives simultaneous coverage at ALL stopping times
    for the declared finite family. Fractional losses are allowed.
    """
    n = int(row['shots'])
    s = float(row['s'])
    if n <= 0 or n != row['shots'] or not 0<=s<=n or not 0<cl<1 or int(family_size)!=family_size or family_size<1:
        raise ValueError('invalid confidence sequence arguments')
    mean = s/n
    constant = betaln(s+.5,n-s+.5)-betaln(.5,.5)-np.log(family_size/(1-cl))
    def root(p):
        return constant-xlogy(s,p)-xlogy(n-s,1-p)
    lo = 0. if s==0 else brentq(root,np.nextafter(0.,1.),mean,xtol=1e-15)
    hi = 1. if s==n else brentq(root,mean,np.nextafter(1.,0.),xtol=1e-15)
    return float(lo), float(hi)


def bulk_design(d, p):
    d, p = np.broadcast_arrays(np.asarray(d, float), np.asarray(p, float))
    z, l = (d-7)/2, np.log(p/1e-4)
    return np.stack([np.ones_like(z), z, l, z*l], axis=-1)


def window_design(d, p, alt=False):
    d, p = np.broadcast_arrays(np.asarray(d, float), np.asarray(p, float))
    cols = [np.ones_like(d), np.log(p/1e-4)]
    if alt:
        cols.append((d-7)/2)
    return np.stack(cols, axis=-1)


def category_probabilities(bulk, d, p, window=None):
    """Two category intensities, normalized with the zero category baseline.

    quiet: r_j=exp(X theta_j); noisy: r_j=bulk_j+exp(Z phi_j).
    P=(1,r_half,r_one)/(1+r_half+r_one). This is an explicit model,
    not the old scalar power-law with a fictitious count distribution.
    """
    X = bulk_design(d, p)
    log_rates = X @ np.asarray(bulk).reshape(2, 4).T
    if window is not None:
        window = np.asarray(window)
        Z = window_design(d, p, alt=(window.size == 6))
        log_rates = np.logaddexp(log_rates, Z @ window.reshape(2, -1).T)
    logits = np.concatenate([np.zeros(log_rates.shape[:-1]+(1,)), log_rates], axis=-1)
    return np.exp(logits-logsumexp(logits, axis=-1, keepdims=True))


def mean_infidelity(bulk, d, p, window=None):
    pr = category_probabilities(bulk, d, p, window)
    return .5*pr[..., 1]+pr[..., 2]


@dataclass
class FitResult:
    parameters: np.ndarray
    diagnostics: dict


def _fit(df, observed=None, bulk=None, alt=False, start=None):
    observed = counts(df) if observed is None else np.asarray(observed)
    n = df.shots.to_numpy(float)
    if observed.shape != (len(df), 3) or np.any(observed < 0) or not np.allclose(observed.sum(axis=1), n):
        raise ValueError('multinomial counts do not sum to shots')
    if len(df) == 0:
        raise ValueError('empty fit')
    X = bulk_design(df.d.values, df.p.values) if bulk is None else window_design(df.d.values, df.p.values, alt)
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise ValueError('rank deficient model design')
    width = X.shape[1]
    B = None if bulk is None else bulk_design(df.d.values, df.p.values) @ np.asarray(bulk).reshape(2,4).T
    def objective(theta):
        W = X @ theta.reshape(2, width).T
        eta = W if B is None else np.logaddexp(B, W)
        logits = np.column_stack([np.zeros(len(df)), eta])
        logpr = logits-logsumexp(logits, axis=1, keepdims=True)
        value = -float(np.sum(observed*logpr))
        residual = n[:,None]*np.exp(logpr[:,1:])-observed[:,1:]
        if B is not None:
            residual *= expit(W-B)
        gradient = (residual.T @ X).reshape(-1)
        return value, gradient
    initial = np.concatenate([np.linalg.lstsq(X, np.log((observed[:, j]+.5)/(n+1)), rcond=None)[0] for j in [1,2]])
    starts = [np.asarray(start)] if start is not None else [initial]
    flat = np.zeros((2,width)); flat[:,0] = np.log((observed[:,1:].sum(axis=0)+.5)/(n.sum()+1))
    starts += [flat.reshape(-1)]
    attempts = []
    valid = []
    for x0 in starts:
        opt = minimize(objective, np.clip(x0,-45,45), method='L-BFGS-B', jac=True,
                       bounds=[(-50.,50.)]*(2*width), options={'maxiter':2000,'ftol':1e-13,'gtol':1e-6,'maxls':50})
        finite = bool(np.isfinite(opt.fun) and np.isfinite(opt.x).all())
        attempts.append(dict(success=bool(opt.success), message=str(opt.message), nll=float(opt.fun),
                             iterations=int(opt.nit), finite=finite))
        if opt.success and finite:
            valid.append(opt)
    if not valid:
        raise RuntimeError(f'multinomial optimization failed: {attempts}')
    best = min(valid, key=lambda x:x.fun)
    return FitResult(best.x, dict(success=True, nll=float(best.fun), attempts=attempts,
                     boundary=bool(np.any(np.abs(best.x)>49.9)),
                     category_counts=observed.sum(axis=0).astype(int).tolist(), rank=int(np.linalg.matrix_rank(X))))


def fit_bulk(df, observed=None, start=None):
    return _fit(df, observed, start=start)


def fit_window(df, bulk, observed=None, alt=False, start=None):
    return _fit(df, observed, bulk, alt, start)


def multinomial_sample(df, probabilities, rng):
    return np.array([rng.multinomial(int(n), pr) for n, pr in zip(df.shots, probabilities)], dtype=np.int64)


def fit_models(main, quiet, scenarios, n_boot=200, seed=20261103, window_dmin=7):
    if n_boot < 1:
        raise ValueError('at least one bootstrap replication is required')
    fits, diagnostics = {}, []
    rng = np.random.default_rng(seed)
    for scenario in scenarios:
        q = quiet[quiet.scenario == scenario]
        noisy = main[main.scenario == scenario]
        datasets = [noisy[noisy.d>=window_dmin], noisy[noisy.d>=5], noisy[noisy.d>=5]]
        if q.d.nunique()<3 or q.p.nunique()<2 or q.n_fail.sum()<20:
            raise ValueError(f'insufficient bulk data for {scenario}')
        b = fit_bulk(q)
        windows = [fit_window(ds, b.parameters, alt=(i==1)) for i,ds in enumerate(datasets)]
        central = (b.parameters, *(x.parameters for x in windows))
        diagnostics += [dict(scenario=scenario, replication='central', component='bulk', **b.diagnostics)]
        diagnostics += [dict(scenario=scenario, replication='central', component=name, **x.diagnostics)
                        for name,x in zip(['main','altW','W5'], windows)]
        pq = category_probabilities(b.parameters,q.d.values,q.p.values)
        pn = [category_probabilities(b.parameters, ds.d.values, ds.p.values, w.parameters) for ds,w in zip(datasets,windows)]
        boot = []
        for iteration in range(n_boot):
            bb = fit_bulk(q,multinomial_sample(q,pq,rng),start=b.parameters)
            ws = [fit_window(ds,bb.parameters,multinomial_sample(ds,pr,rng),alt=(i==1),start=w.parameters)
                  for i,(ds,pr,w) in enumerate(zip(datasets,pn,windows))]
            boot.append((bb.parameters, *(x.parameters for x in ws)))
            diagnostics += [dict(scenario=scenario,replication=iteration,component='bulk',**bb.diagnostics)]
            diagnostics += [dict(scenario=scenario,replication=iteration,component=name,**x.diagnostics)
                            for name,x in zip(['main','altW','W5'],ws)]
        fits[scenario] = dict(central=central,boot=boot,p_min_bulk=float(q.p.min()),
                              d_max_data=int(noisy.d.max()),n_boot=n_boot)
    return fits, diagnostics


def model_epsilon(fits, scenario, d, p, window='noisy', params=None, variant='main'):
    pr = fits[scenario]['central'] if params is None else params
    idx = ['main','altW','W5'].index(variant)+1
    return float(mean_infidelity(pr[0],d,p,None if window=='quiet' else pr[idx]))


def data_decision(row, target, cl=.95, family_size=1):
    lo, hi = anytime_mean_cs(row,cl,family_size)
    decision = 'data_certified' if hi<=target else 'data_rejected' if lo>target else 'unresolved'
    return dict(status=decision, lower=lo, upper=hi, confidence=cl, family_size=int(family_size))


def write_diagnostics(path, diagnostics):
    import json
    from pathlib import Path
    Path(path).write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2),encoding='utf-8')
