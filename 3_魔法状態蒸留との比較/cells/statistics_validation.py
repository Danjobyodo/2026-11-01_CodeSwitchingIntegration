import json,os
import numpy as np,pandas as pd
from scipy.stats import multinomial
import analysis_v13 as stats
checks={}
n=48440
lo,hi=stats.bounded_mean_ci({'shots':n,'s':0})
assert abs(hi-(-np.expm1(-np.log(40)/n)))<1e-12
assert hi>7.6e-5
checks['zero_failure_bound']=True
N=18
outcomes=np.array([(N-h-o,h,o) for h in range(N+1) for o in range(N-h+1)])
intervals=np.array([stats.bounded_mean_ci({'shots':N,'s':.5*h+o}) for _,h,o in outcomes])
coverage=[]
for ph,p1 in [(0,.01),(0,.1),(.1,0),(.15,.03),(.5,.2),(.01,.8)]:
    mu=p1+.5*ph
    keep=(intervals[:,0]<=mu)&(mu<=intervals[:,1])
    value=float(multinomial.pmf(outcomes,N,[1-ph-p1,ph,p1])[keep].sum())
    assert value>=.95-1e-12
    coverage.append(value)
checks['exact_fixed_sample_coverage']=coverage
# Enumerate Bernoulli path probabilities, pruning paths at first CS failure.
optional_failures=[]
for p in [.01,.1,.5]:
    alive=np.array([1.]);failed=0.
    for n in range(1,101):
        nxt=np.zeros(n+1);nxt[:-1]+=alive*(1-p);nxt[1:]+=alive*p
        for k in range(n+1):
            lo,hi=stats.anytime_mean_cs({'shots':n,'s':k})
            if not lo<=p<=hi:failed+=nxt[k];nxt[k]=0
        alive=nxt
    assert failed<=.05+1e-12
    optional_failures.append(float(failed))
checks['optional_stopping_failure_probabilities']=optional_failures
# Categories, rather than fictitious independent half-failures, are sampled.
grid=pd.DataFrame([(d,p,100000) for d in [3,5,7,9] for p in [1e-4,3e-4,1e-3]],columns=['d','p','shots'])
truth=np.array([-7.,-.7,1.8,.05,-6.,-.8,2.,.1])
pr=stats.category_probabilities(truth,grid.d,grid.p)
obs=stats.multinomial_sample(grid,pr,np.random.default_rng(42))
assert np.all(obs.sum(axis=1)==grid.shots)
fit=stats.fit_bulk(grid,obs)
assert fit.diagnostics['success']
assert np.max(np.abs(stats.category_probabilities(fit.parameters,grid.d,grid.p)-pr))<.005
checks['multinomial_fit']=True
os.makedirs('results_v13',exist_ok=True)
with open('results_v13/statistics_validation.json','w') as file:json.dump(checks,file,indent=2)
print(json.dumps(checks,indent=2))
print('STATISTICS VALIDATION PASSED')
