import unittest,sys,types,json,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load_torus():
    p=ROOT/'1_D4閾値/tools_v13/cells';m=types.ModuleType('d4_v13_tests');sys.modules[m.__name__]=m
    for name in ['c02_config_main','c03_geometry','c04_depol','c05_pheno','c06_cl','c07_tf','c08_protocol','c09_dispatch','v02_config_val','v10_dense','v11_run','v13_proxy']:
        exec(compile((p/(name+'.py')).read_text(),name,'exec'),m.__dict__)
    return m

class PhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.m=load_torus()
    def test_proxy_three_noise_models(self):
        for L in [3,5,7,9]:
            for model,p in [('depolarizing',.1),('phenomenological',.04),('circuit_level',.005)]:
                result=self.m.proxy_crosscheck(model,L,p,3,20261103)
                self.assertEqual(result['max_prob_deviation'],0)
                self.assertEqual(result['max_fidelity_deviation'],0)
    def test_resume_does_not_resample_and_rejects_configuration_change(self):
        m=self.m
        old=dict(m.CFG);real=m.run_one_point
        with tempfile.TemporaryDirectory() as out:
            m.CFG.update(out_dir=out,L_values=[3],p_n=1,p_min=.001,p_max=.001,shots=4,
                         noise_model='depolarizing',save_pdf=False,run_self_checks=False,
                         print_geometry_summary=False,resume=True,out_csv=None,out_png=None)
            try:
                first=m.run_experiments()
                m.run_one_point=lambda **kw: (_ for _ in ()).throw(AssertionError('resampled'))
                second=m.run_experiments()
                self.assertEqual(first.to_json(),second.to_json())
                # CSV is a derivative: reconstruct after a missing/partial export.
                for csv in Path(out).glob('*X_memory*.csv'):csv.write_text('interrupted export')
                third=m.run_experiments();self.assertEqual(first.to_json(),third.to_json())
                m.CFG['seed']+=1
                with self.assertRaises(ValueError):m.run_experiments()
            finally:m.run_one_point=real;m.CFG.clear();m.CFG.update(old)
    def test_shared_notebook_definitions(self):
        import ast
        maps=[]
        for name in ['D4_v13_main.ipynb','D4_v13_validation.ipynb']:
            definitions={}
            for cell in json.loads((ROOT/'1_D4閾値'/name).read_text())['cells']:
                if cell['cell_type']!='code':continue
                try:tree=ast.parse(''.join(cell['source']))
                except SyntaxError:continue
                for node in tree.body:
                    if isinstance(node,(ast.FunctionDef,ast.ClassDef)):definitions[node.name]=ast.dump(node)
            maps.append(definitions)
        for name in maps[0].keys()&maps[1].keys():self.assertEqual(maps[0][name],maps[1][name],name)
    def test_plane_geometry_mapping(self):
        sys.path.insert(0,str(ROOT/'2_CodeSwitching論理誤り率'))
        import chsc_switch_v13 as c
        mod=types.ModuleType('plane_reference');sys.modules[mod.__name__]=mod
        for f in ['common_lib.py','d4_lib.py']:
            exec(compile((ROOT/'旧版'/'3_魔法状態蒸留との比較_v5_2'/'tools'/f).read_text(),f,'exec'),mod.__dict__)
        for d in [2,3,5,7,9]:
            a=c.TriangleCode(d);lat=mod.D4Lattice(d);b=mod.CodeData(lat)
            frozen={q for lab,qs in lat.z_checks() if lab[0]=='bdZ' and len(qs)==1 for q in qs}
            mp={i:3*lat.eidx[a.edges[e]]+mod.CNAME.index(col) for i,(e,col) in enumerate(a.qubits)}
            A={(frozenset(mp[q] for q in g.supp),frozenset(tuple(sorted((mp[x],mp[y]))) for x,y in g.pairs)) for g in a.gens}
            B={(op.s-frozen,frozenset(pr for pr in op.quad if not set(pr)&frozen)) for _,op in b.xgens}
            self.assertEqual(A,B)
            self.assertEqual({frozenset(mp[q] for q in qs) for _,_,qs in a.zchecks},
                             {frozenset(qs)-frozen for _,qs in lat.z_checks()}-{frozenset()})
if __name__=='__main__':unittest.main()
