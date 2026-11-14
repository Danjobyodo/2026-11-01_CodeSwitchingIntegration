"""v11/v12/v13: results written by an equivalent earlier version under its own file name are continued, not recomputed,
and (v12 and later) the drivers write only the files the study needs.

Study 2: v10 accepted the conditions of a v9 CSV but opened only chsc_v10_*.csv, so the existing production file
chsc_v9_*.csv was not found by the driver.  Study 1: the v13 checkpoint name differs from the v12, v11 and v10 ones.
v13 (labels and output names only) also accepts the v12 files of both studies.
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
        import chsc_switch_v13 as c
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
                new = Path(out)/'chsc_v13_in_T_out_noisy.csv'
                self.assertTrue(new.exists())
                self.assertEqual(len(first), 24)
                self.assertEqual(int(first.shots.sum()), 480000)
                self.assertEqual(copy.read_bytes(), before)                 # earlier file untouched
                old = pd.read_csv(copy).sort_values(['d', 'p']).reset_index(drop=True)
                self.assertTrue((old.n_I.to_numpy() == first.sort_values(['d', 'p']).n_I.to_numpy()).all())
                # v12: per condition only the CSV and the manifest; one crossings table and one figure for out_dir
                self.assertEqual(sorted(f.name for f in Path(out).iterdir()),
                                 sorted([self.legacy.name, 'chsc_v13_in_T_out_noisy.csv', 'chsc_v13_in_T_out_noisy_manifest.json',
                                         'chsc_v13_crossings.csv', 'chsc_v13_P_L.png']))
                cr = pd.read_csv(Path(out)/'chsc_v13_crossings.csv')
                self.assertEqual(sorted(zip(cr.d_a, cr.d_b)), [(3, 5), (5, 7)])
                second = c.run_experiments(self.cfg(out))                  # now from the v13 file
                self.assertEqual(first.to_json(), second.to_json())
            finally:
                c.run_point = real

    def test_v12_file_name_is_reused(self):
        # v13: a result file written by v12 (chsc_v12_*.csv) is continued as well
        c = self.c
        real = c.run_point
        with tempfile.TemporaryDirectory() as out:
            shutil.copy(self.legacy, Path(out)/'chsc_v12_in_T_out_noisy.csv')
            c.run_point = no_sampling
            try:
                res = c.run_experiments(self.cfg(out))
                self.assertEqual(int(res.shots.sum()), 480000)
                self.assertTrue((Path(out)/'chsc_v13_in_T_out_noisy.csv').exists())
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
                self.assertFalse((Path(out)/'chsc_v13_in_T_out_noisy.csv').exists())
                shutil.copy(self.legacy, Path(out)/'chsc_v10_in_T_out_noisy.csv')
                with self.assertRaises(ValueError):                         # two earlier files: not merged silently
                    c.run_experiments(self.cfg(out))
        finally:
            c.run_point = real


class Study1LegacyCheckpoint(unittest.TestCase):
    def test_v12_v11_and_v10_checkpoints_are_continued(self):
        p = ROOT/'1_D4閾値/tools_v13/cells'
        m = types.ModuleType('d4_v13_legacy_tests'); sys.modules[m.__name__] = m
        for name in ['c02_config_main', 'c03_geometry', 'c04_depol', 'c05_pheno', 'c06_cl', 'c07_tf', 'c08_protocol', 'c09_dispatch']:
            exec(compile((p/(name + '.py')).read_text(), name, 'exec'), m.__dict__)
        old = dict(m.CFG); real = m.run_one_point
        with tempfile.TemporaryDirectory() as out:
            m.CFG.update(out_dir=out, L_values=[3], p_n=2, p_min=.001, p_max=.002, shots=4, noise_model='depolarizing',
                         run_self_checks=False, print_geometry_summary=False, resume=True, out_csv=None, out_png=None)
            try:
                first = m.run_experiments()
                tag = 'd4_v13_X_memory_depolarizing_twisted_frame'
                # v12 and later: one run = CSV, one figure (3 metrics), crossings, manifest, checkpoint (no PDF by default)
                self.assertEqual(sorted(f.name for f in Path(out).iterdir()),
                                 sorted(tag + s for s in ('.csv', '.png', '_crossings.csv', '_manifest.json', '_checkpoint.json')))
                ck = Path(out)/(tag + '_checkpoint.json')
                record = json.loads(ck.read_text())
                self.assertEqual(record['config']['code_version'], 'd4_v13')
                for version in ('d4_v12', 'd4_v11', 'd4_v10'):               # what v12 / v11 / v10 wrote for the same configuration
                    rec = dict(record, config=dict(record['config'], code_version=version))
                    legacy = ck.with_name(ck.name.replace('d4_v13_', version + '_', 1))
                    for f in list(Path(out).iterdir()):
                        f.unlink()
                    legacy.write_text(json.dumps(rec))
                    before = legacy.read_bytes()
                    m.run_one_point = no_sampling
                    second = m.run_experiments()
                    m.run_one_point = real
                    self.assertEqual(first.to_json(), second.to_json(), version)
                    self.assertTrue(ck.exists())
                    self.assertEqual(legacy.read_bytes(), before)
                ck.unlink()
                for f in Path(out).glob('d4_v13_*'):
                    f.unlink()
                m.CFG['seed'] += 1
                m.run_one_point = no_sampling
                with self.assertRaises(ValueError):                         # anything but the label differs -> refused
                    m.run_experiments()
            finally:
                m.run_one_point = real; m.CFG.clear(); m.CFG.update(old)

if __name__ == '__main__':
    unittest.main()
