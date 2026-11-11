import unittest,sys
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import binom,multinomial
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'3_魔法状態蒸留との比較'))
import analysis_v12 as a

class StatisticsTests(unittest.TestCase):
    def test_zero_and_half_only(self):
        n=48440
        self.assertAlmostEqual(a.bounded_mean_ci({'shots':n,'s':0})[1],-np.expm1(-np.log(40)/n),places=14)
        self.assertGreater(a.anytime_mean_cs({'shots':n,'s':0})[1],a.bounded_mean_ci({'shots':n,'s':0})[1])
        lo,hi=a.bounded_mean_ci({'shots':100,'s':50})
        self.assertLess(lo,.5);self.assertGreater(hi,.5)
        self.assertEqual(a.anytime_mean_cs({'shots':10,'s':10})[1],1)
    def test_exact_finite_sample_coverage(self):
        # Enumerate every possible multinomial result, not just a passing seed.
        n=18
        outcomes=np.array([(n-i-j,i,j) for i in range(n+1) for j in range(n-i+1)])
        intervals=np.array([a.bounded_mean_ci({'shots':n,'s':h*.5+one}) for _,h,one in outcomes])
        for ph,p1 in [(0,.01),(0,.1),(.1,0),(.15,.03),(.5,.2),(.01,.8)]:
            mu=p1+.5*ph
            covered=(intervals[:,0]<=mu)&(mu<=intervals[:,1])
            mass=multinomial.pmf(outcomes,n,[1-ph-p1,ph,p1])
            self.assertGreaterEqual(float(mass[covered].sum()),.95-1e-12)
    def test_optional_stopping_sequence(self):
        # Exact probability recursion for Bernoulli paths up to N=100.
        for p in [.01,.1,.5]:
            alive=np.array([1.]);failed=0.
            for n in range(1,101):
                nxt=np.zeros(n+1);nxt[:-1]+=alive*(1-p);nxt[1:]+=alive*p
                for k in range(n+1):
                    lo,hi=a.anytime_mean_cs({'shots':n,'s':k})
                    if not lo<=p<=hi:failed+=nxt[k];nxt[k]=0
                alive=nxt
            self.assertLessEqual(failed,.05+1e-12)
    def test_reference_validation_and_duplicates(self):
        raw=pd.read_csv(ROOT/'3_魔法状態蒸留との比較/data/d4_noisy_mc.csv')
        g=a.aggregate_counts(raw)
        row=g[(g.scenario=='B')&(g.window=='noisy')&(g.d==5)&(g.p==1e-4)&(g.kappa0==1)&(g.kappa_in==1)&(g.kappa_out==1)].iloc[0]
        self.assertEqual(row.shots,414400);self.assertEqual(row.n_one,12)
        with self.assertRaises(ValueError):a.aggregate_counts(pd.concat([raw,raw.iloc[:1]]))
        bad=raw.copy();bad.loc[0,'sum_infidelity']+=.5
        with self.assertRaises(ValueError):a.aggregate_counts(bad)
        bad_rounds=raw.copy();bad_rounds.loc[0,'Rin']+=1
        with self.assertRaises(ValueError):a.aggregate_counts(bad_rounds)
        copied=raw.iloc[:1].copy();copied['run_id']='copied-run'
        with self.assertRaises(ValueError):a.aggregate_counts(pd.concat([raw,copied]))
    def test_multinomial_fit_and_bootstrap(self):
        grid=pd.DataFrame([(d,p,100000) for d in [3,5,7,9] for p in [1e-4,3e-4,1e-3]],columns=['d','p','shots'])
        theta=np.array([-7.,-.7,1.8,.05,-6.,-.8,2.,.1])
        prob=a.category_probabilities(theta,grid.d,grid.p)
        obs=a.multinomial_sample(grid,prob,np.random.default_rng(42))
        self.assertTrue(np.all(obs.sum(axis=1)==grid.shots))
        fit=a.fit_bulk(grid,obs)
        self.assertTrue(fit.diagnostics['success'])
        prediction=a.category_probabilities(fit.parameters,grid.d,grid.p)
        self.assertLess(np.max(np.abs(prediction-prob)),.005)
        with self.assertRaises(ValueError):a.fit_bulk(grid,obs+1)
    def test_family_and_no_model_override(self):
        row={'shots':10000,'s':0}
        self.assertGreater(a.anytime_mean_cs(row,family_size=200)[1],a.anytime_mean_cs(row)[1])
        self.assertEqual(a.data_decision(row,1e-5)['status'],'unresolved')
        self.assertEqual(a.data_decision(row,1e-2)['status'],'data_certified')

if __name__=='__main__':unittest.main()
