"""v10 (unchanged in v11): data certificates of study 3 use the per-decision family (candidate sizes of one row);
the v9.2 table-wide family is a stricter sensitivity. Checks the logic on the stored reference data."""
import sys, unittest
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'3_魔法状態蒸留との比較'))
import analysis_v11 as a


class DecisionFamilyTests(unittest.TestCase):
    def setUp(self):
        raw = pd.read_csv(ROOT/'3_魔法状態蒸留との比較/data/d4_noisy_mc.csv')
        g = a.aggregate_counts(raw)
        k1 = (g.kappa0 == 1) & (g.kappa_in == 1) & (g.kappa_out == 1)
        self.main = g[k1 & (g.window == 'noisy')]

    def row(self, s, d, p):
        r = self.main[(self.main.scenario == s) & (self.main.d == d) & np.isclose(self.main.p, p)]
        self.assertEqual(len(r), 1)
        return r.iloc[0]

    def test_family_size_is_number_of_candidate_sizes(self):
        sub = self.main[(self.main.scenario == 'B') & np.isclose(self.main.p, 1e-4)]
        self.assertEqual(sorted(sub.d.unique().tolist()), [3, 5, 7, 9])

    def test_tablewide_is_stricter(self):
        r = self.row('B', 5, 1e-4)
        self.assertLess(a.anytime_mean_cs(r, family_size=4)[1], a.anytime_mean_cs(r, family_size=200)[1])

    def test_reference_decision_B_p1e4(self):
        # d=3 rejected, d=5 certified for target 1e-4 with the per-decision family (4 candidate sizes);
        # not certified with the table-wide family of 200 (v9.2).
        self.assertEqual(a.data_decision(self.row('B', 3, 1e-4), 1e-4, .95, 4)['status'], 'data_rejected')
        self.assertEqual(a.data_decision(self.row('B', 5, 1e-4), 1e-4, .95, 4)['status'], 'data_certified')
        self.assertEqual(a.data_decision(self.row('B', 5, 1e-4), 1e-4, .95, 200)['status'], 'unresolved')

    def test_tablewide_lower_bound_equals_decision_family_at_target_1e4(self):
        # v11: 'at least x times in all ten conditions' is a statement about the whole table.  The smallest size that
        # is not data-rejected at target 1e-4 is the same with the table-wide family (200) as with the row family (4).
        expected = {('B', 1e-4): 5, ('B', 2e-4): 5, ('B', 3e-4): 5, ('B', 5e-4): 7, ('B', 1e-3): 11,
                    ('A', 1e-4): 7, ('A', 2e-4): 9, ('A', 3e-4): 11, ('A', 5e-4): 11, ('A', 1e-3): 11}
        for (s, p), d_low in expected.items():
            for family in (4, 200):
                rejected = [d for d in (3, 5, 7, 9)
                            if a.data_decision(self.row(s, d, p), 1e-4, .95, family)['status'] == 'data_rejected']
                possible = [d for d in range(3, 62, 2) if d not in rejected]
                self.assertEqual(min(possible), d_low, (s, p, family))


if __name__ == '__main__':
    unittest.main()
