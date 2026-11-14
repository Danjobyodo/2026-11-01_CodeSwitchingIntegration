import ast,json,sys,types,tempfile,unittest
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def publication_patches():
    """The comment / dead-code patches that build_notebooks_v13.py applies to the v9 notebooks (publication cleanup)."""
    ns={'__name__':'builder','__file__':str(ROOT/'3_魔法状態蒸留との比較'/'build_notebooks_v13.py')}
    exec(compile((ROOT/'3_魔法状態蒸留との比較'/'build_notebooks_v13.py').read_text(),'build_notebooks_v13.py','exec'),ns)
    return ns['PUB_COMMENT']+ns['PUB_CODE']

def definitions(path,patches=()):
    result={}
    for cell in json.loads(path.read_text())['cells']:
        if cell['cell_type']!='code':continue
        text=''.join(cell['source'])
        for old,new in patches:text=text.replace(old,new)
        try:tree=ast.parse(text)
        except SyntaxError:continue
        for node in tree.body:
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)):result[node.name]=ast.dump(node)
    return result

class NotebookTests(unittest.TestCase):
    def test_preserved_physical_definitions(self):
        for name in ['D4_noisy_simulation.ipynb','noisy_cost_comparison.ipynb','validation.ipynb']:
            # v9 definitions with exactly the publication patches of the builder applied: nothing else may differ
            old=definitions(ROOT/'旧版'/'3_魔法状態蒸留との比較_v9'/name,publication_patches())
            new=definitions(ROOT/'3_魔法状態蒸留との比較'/name)
            # Only analysis helpers and the MC stopping rule change, not gates/noise/decoders.
            changed={'calibrate','run_point','fit_bulk','fit_window','eps_K_model','eps_ci','model_allowed','point_data','kob_entry','decide','win_eps','bulk_eps','_design_bulk','identifiable'}
            for key in old.keys()&new.keys()-changed:self.assertEqual(old[key],new[key],key)
    def test_fixed_shot_worker(self):
        nb=json.loads((ROOT/'3_魔法状態蒸留との比較/D4_noisy_simulation.ipynb').read_text())
        source=next(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code' and 'def run_point(pt, base_seed)' in ''.join(c['source']))
        tree=ast.parse(source)
        functions=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[])
        class Ex:
            def __init__(self,*args,**kw):pass
            def run(self,n,rng):return np.ones(n),[dict(n_err=1,so_cz=0) for _ in range(n)]
        import time,threading
        with tempfile.TemporaryDirectory() as tmp:
            ns=dict(np=np,pd=pd,time=time,os=__import__('os'),D4Experiment=Ex,NoiseModel=lambda *args,**kwargs:None,
                    done=None,_LOCK=threading.Lock(),MC_CSV=str(Path(tmp)/'out.csv'),RUN_ID='test',SHOTS_PER_POINT=13,EXTEND_SHOTS=7)
            # Deterministic all-failure mock checks the stopping rule.
            def run(self,n,rng):return np.ones(n),[dict(n_err=1,so_cz=0) for _ in range(n)]
            Ex.run=run
            exec(compile(functions,'worker','exec'),ns)
            pt=dict(scenario='B',d=7,p=.001,p_idle=0,kappa=(1,1,1))
            ns['run_point'](pt,123)
            first=pd.read_csv(ns['MC_CSV']);self.assertEqual(int(first.shots.sum()),13)
            # All shots fail: still complete the fixed quota, then a no-op resume.
            ns['done']=first;ns['run_point'](pt,123)
            self.assertEqual(pd.read_csv(ns['MC_CSV']).shape,first.shape)
            ns['run_point']({**pt,'extend':True},123)
            result=pd.read_csv(ns['MC_CSV']);self.assertEqual(int(result.shots.sum()),20)
            self.assertEqual(result.seed.nunique(),len(result))
    def test_extend_appends_to_stored_production_format(self):
        # v11: the stored production CSV has no stopping_rule column; v9.2/v10 appended rows with that extra column
        # and the file could no longer be read.  Extend the real header and read the result back.
        nb=json.loads((ROOT/'3_魔法状態蒸留との比較/D4_noisy_simulation.ipynb').read_text())
        source=next(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code' and 'def run_point(pt, base_seed)' in ''.join(c['source']))
        self.assertIn("MC_COLUMNS = list(done.columns) if done is not None else None",source)
        functions=ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)],type_ignores=[])
        class Ex:
            def __init__(self,*args,**kw):pass
            def run(self,n,rng):return np.zeros(n),[dict(n_err=1,so_cz=0) for _ in range(n)]
        import time,threading
        stored=pd.read_csv(ROOT/'3_魔法状態蒸留との比較/data/d4_noisy_mc.csv')
        self.assertNotIn('stopping_rule',stored.columns)
        pid='B|noisy|d7|p0.0002|pi0|k1,1,1'
        old=stored[stored.point_id==pid];self.assertGreater(len(old),0)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'mc.csv';old.to_csv(path,index=False)
            done=pd.read_csv(path)
            ns=dict(np=np,pd=pd,time=time,os=__import__('os'),D4Experiment=Ex,NoiseModel=lambda *args,**kwargs:None,
                    done=done,MC_COLUMNS=list(done.columns),_LOCK=threading.Lock(),MC_CSV=str(path),RUN_ID='extension-test',
                    SHOTS_PER_POINT=13,EXTEND_SHOTS=250)
            exec(compile(functions,'worker','exec'),ns)
            ns['run_point'](dict(scenario='B',d=7,p=2e-4,p_idle=0.0,kappa=(1.0,1.0,1.0),extend=True),123)
            result=pd.read_csv(path)                       # must parse
            self.assertEqual(list(result.columns),list(stored.columns))
            self.assertEqual(int(result.shots.sum()),int(old.shots.sum())+250)
            new=result[result.run_id=='extension-test']
            self.assertEqual(int(new.chunk_id.min()),int(old.chunk_id.max())+1)
            self.assertFalse(result.duplicated(['scenario','window','d','p','seed']).any())
            self.assertTrue(np.allclose(new.sum_infidelity,new.n_fail-.5*new.n_half))

    def test_existing_calibration_is_preserved(self):
        nb=json.loads((ROOT/'3_魔法状態蒸留との比較/D4_noisy_simulation.ipynb').read_text())
        src=next(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code' and 'def calibrate()' in ''.join(c['source']))
        tree=ast.parse(src)
        fun=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[])
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'cal.csv';path.write_text('scenario,pL_per_round\nB,0.001\n')
            before=path.read_bytes();ns=dict(os=__import__('os'),pd=pd,CAL_CSV=str(path))
            exec(compile(fun,'calibrate','exec'),ns)
            result=ns['calibrate']()
            self.assertEqual(len(result),1);self.assertEqual(path.read_bytes(),before)

    def test_study2_recomputed_metrics(self):
        p=ROOT/'2_CodeSwitching論理誤り率/summarize_results_v13.py'
        ns={'__name__':'summary_test','__file__':str(p)};exec(compile(p.read_text(),str(p),'exec'),ns)
        with tempfile.TemporaryDirectory() as tmp:
            result=ns['summarize'](tmp);self.assertEqual(len(result),144)
            self.assertEqual(int(result.shots.sum()),2880000)

if __name__=='__main__':unittest.main()
