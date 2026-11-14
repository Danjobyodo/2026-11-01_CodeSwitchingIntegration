"""v13: the figures of study 3 are drawn from the stored result CSVs by figures_v13.py and decide nothing themselves."""
import json, sys, tempfile, unittest
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
ROOT = Path(__file__).resolve().parents[1]
S3 = ROOT/'3_魔法状態蒸留との比較'
sys.path.insert(0, str(S3))
import figures_v13 as figs


class FigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames = figs.load(str(S3/'results_v13'))

    def test_pareto_front_is_the_set_of_undominated_candidates(self):
        fac = self.frames['factories']
        df = fac[(fac.scenario == 'B') & np.isclose(fac.p, 1e-4)]
        front = figs.pareto_front(df)
        self.assertTrue((np.diff(front.volume_steps) >= 0).all() and (np.diff(front.eps) < 0).all())
        for _, r in df.iterrows():      # every candidate is matched or beaten by a member of the front
            self.assertTrue(((front.volume_steps <= r.volume_steps) & (front.eps <= r.eps)).any())
        # the cheapest factory of the comparison table for each target lies on the front
        cmp_ = self.frames['comparison']
        for _, r in cmp_[(cmp_.scenario == 'B') & np.isclose(cmp_.p, 1e-4)].iterrows():
            self.assertTrue(np.isclose(front.volume_steps, r.litinski_volume).any())

    def test_notes_quote_the_comparison_table(self):
        cmp_ = self.frames['comparison']
        at = cmp_[np.isclose(cmp_.target, 1e-4)]
        certified = at[(at.scenario == 'B') & np.isclose(at.p, 1e-4)].iloc[0]
        note = figs.target_note(certified)
        self.assertIn('$d$ = 5 certified by data', note)
        self.assertIn(f'{certified.ratio_kobayashi_over_litinski:.2f}', note)
        self.assertEqual(f'{certified.ratio_kobayashi_over_litinski:.2f}', '2.30')
        for _, r in at[at.kobayashi_status != 'data_certified'].iterrows():
            note = figs.target_note(r)
            self.assertIn('no $d \\leq 9$ certified', note)
            self.assertIn(f'{r.ratio_kobayashi_low_over_litinski:.2f}', note)
        self.assertEqual(f'{at.ratio_kobayashi_low_over_litinski.min():.2f}', '1.59')

    def test_every_simulated_point_is_drawable(self):
        # a point without failures has eps = 0 (not drawable on a log axis): it is drawn at the upper end of its interval
        iv = self.frames['intervals']
        self.assertTrue((iv.upper_decision > 0).all())
        self.assertTrue((iv.lower_decision[iv.s > 0] > 0).all())
        zero = figs.standard_points(iv, 'B', 'noisy')
        zero = zero[(zero.s == 0)]
        self.assertEqual([(int(r.d), float(r.p)) for _, r in zero.iterrows()], [(9, 1e-4)])

    def test_curves_are_the_central_model_of_the_prediction_table(self):
        curves, pred = self.frames['curves'], pd.read_csv(S3/'results_v13/model_predictions.csv')
        vs_d = curves[curves.curve == 'vs_d']
        merged = pred.merge(vs_d, on=['scenario', 'window', 'd', 'p'])
        self.assertEqual(len(merged), len(pred))
        self.assertTrue(np.allclose(merged.eps_model_x, merged.eps_model_y, rtol=1e-12, atol=0))
        self.assertTrue((merged.model_fit_domain == merged.in_fit_domain).all())

    def test_figures_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = figs.make_all(str(S3/'results_v13'), tmp)
            self.assertEqual(sorted(Path(x).name for x in written), ['cost_comparison.png', 'd4_logical_error.png'])
            for x in written:
                self.assertGreater(Path(x).stat().st_size, 50000)

    def test_notebook_embeds_the_current_modules(self):
        nb = json.loads((S3/'noisy_cost_comparison.ipynb').read_text())
        source = ''.join(''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code')
        for name in ('analysis_v13.py', 'figures_v13.py'):
            self.assertIn(repr((S3/name).read_text()), source, name)
        self.assertIn((S3/'cells/figures.py').read_text(), source)
        self.assertNotIn('plt.savefig', source.replace(repr((S3/'figures_v13.py').read_text()), ''))


if __name__ == '__main__':
    unittest.main()
