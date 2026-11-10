"""v11: results written by an equivalent earlier version under its own file name are continued, not recomputed.

Study 2: v10 accepted the conditions of a v9 CSV but opened only chsc_v10_*.csv, so the existing production file
chsc_v9_*.csv was not found by the driver.  Study 1: the v11 checkpoint name differs from the v10 one.
Both tests run the real driver and fail if a point is sampled again."""
import json, shutil, sys, tempfile, types, unittest
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
S2 = ROOT/'2_CodeSwitching論理誤り率'


def no_sampling(*args, **kwargs):
    raise AssertionError('a completed point was sampled again')


class Study2LegacyCsv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(S2))
        import chsc_switch_v11 as c
        cls.c = c
        cls.legacy = S2/'本番結果'/'chsc_v9_results'/'chsc_v9_in_T_out_noisy.csv'

    def cfg(self, out, **kw):
        cfg = dict(self.c.CFG)
        cfg.update(out_dir=out, cases_to_run=['in_T_out'], boundaries_to_run=['noisy'], d_values=[3, 5, 7], shots=20000,
                   run_self_checks=False, save_pdf=False, resume=True)
        cfg.update(kw)
        return cfg

    def test_v9_production_csv_is_reused_by_the_driver(self):
        c = self.c
        real = c.run_point
        with tempfile.TemporaryDirectory() as out:
            copy = Path(out)/self.legacy.name
            shutil.copy(self.legacy, copy)
            before = copy.read_bytes()
            c.run_point = no_sampling
            try:
                first = c.run_experiments(self.cfg(out))
                new = Path(out)/'chsc_v11_in_T_out_noisy.csv'
                self.assertTrue(new.exists())
                self.assertEqual(len(first), 24)
                self.assertEqual(int(first.shots.sum()), 480000)
                self.assertEqual(copy.read_bytes(), before)                 # earlier file untouched
                old = pd.read_csv(copy).sort_values(['d', 'p']).reset_index(drop=True)
                self.assertTrue((old.n_I.to_numpy() == first.sort_values(['d', 'p']).n_I.to_numpy()).all())
                second = c.run_experiments(self.cfg(out))                  # now from the v11 file
                self.assertEqual(first.to_json(), second.to_json())
            finally:
                c.run_point = real

    def test_other_conditions_and_ambiguous_files_are_refused(self):
        c = self.c
        real = c.run_point
        c.run_point = no_sampling
        try:
            with tempfile.TemporaryDirectory() as out:
                shutil.copy(self.legacy, Path(out)/self.legacy.name)
                with self.assertRaises(ValueError):                         # other seed = other samples
                    c.run_experiments(self.cfg(out, seed=int(c.CFG['seed']) + 1))
                self.assertFalse((Path(out)/'chsc_v11_in_T_out_noisy.csv').exists())
                shutil.copy(self.legacy, Path(out)/'chsc_v10_in_T_out_noisy.csv')
                with self.assertRaises(ValueError):                         # two earlier files: not merged silently
                    c.run_experiments(self.cfg(out))
        finally:
            c.run_point = real


class Study1LegacyCheckpoint(unittest.TestCase):
    def test_v10_checkpoint_is_continued(self):
        p = ROOT/'1_D4閾値/tools_v11/cells'
        m = types.ModuleType('d4_v11_legacy_tests'); sys.modules[m.__name__] = m
        for name in ['c02_config_main', 'c03_geometry', 'c04_depol', 'c05_pheno', 'c06_cl', 'c07_tf', 'c08_protocol', 'c09_dispatch']:
            exec(compile((p/(name + '.py')).read_text(), name, 'exec'), m.__dict__)
        old = dict(m.CFG); real = m.run_one_point
        with tempfile.TemporaryDirectory() as out:
            m.CFG.update(out_dir=out, L_values=[3], p_n=2, p_min=.001, p_max=.002, shots=4, noise_model='depolarizing',
                         save_pdf=False, run_self_checks=False, print_geometry_summary=False, resume=True,
                         out_csv=None, out_png=None)
            try:
                first = m.run_experiments()
                ck = next(Path(out).glob('d4_v11_*_checkpoint.json'))
                record = json.loads(ck.read_text())
                self.assertEqual(record['config']['code_version'], 'd4_v11')
                record['config']['code_version'] = 'd4_v10'                 # what v10 wrote for the same configuration
                legacy = ck.with_name(ck.name.replace('d4_v11_', 'd4_v10_', 1))
                for f in list(Path(out).iterdir()):
                    f.unlink()
                legacy.write_text(json.dumps(record))
                before = legacy.read_bytes()
                m.run_one_point = no_sampling
                second = m.run_experiments()
                self.assertEqual(first.to_json(), second.to_json())
                self.assertTrue(ck.exists())
                self.assertEqual(legacy.read_bytes(), before)
                ck.unlink()
                for f in Path(out).glob('d4_v11_*'):
                    f.unlink()
                m.CFG['seed'] += 1
                with self.assertRaises(ValueError):                         # anything but the label differs -> refused
                    m.run_experiments()
            finally:
                m.run_one_point = real; m.CFG.clear(); m.CFG.update(old)


if __name__ == '__main__':
    unittest.main()
