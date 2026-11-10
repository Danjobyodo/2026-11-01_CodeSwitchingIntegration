"""研究 5（より高い階層の code switching）の回帰テスト。
    python -m unittest tests.test_study5 -v
numpy だけで動く（距離の計算だけ scipy を使う。無ければその 1 件を飛ばす）。"""
import ast, importlib.util, json, sys, unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
S5 = ROOT / '5_高階層スイッチングプロトコル'
sys.path.insert(0, str(S5 / 'src'))
import hier_lib as H   # noqa: E402


def code_cells(path):
    return [''.join(c['source']) for c in json.loads(path.read_text(encoding='utf-8'))['cells'] if c['cell_type'] == 'code']


class Study5Structure(unittest.TestCase):
    def test_first_cell_installs_and_second_cell_holds_parameters(self):
        for name, must in (('研究5_main.ipynb', ['RUN_MODE', 'SEED', 'OUT_DIR', 'N_SAMPLES', 'N_TRIALS', 'MAX_D', 'PLAN',
                                                'T_COUNT_COEF', 'BREAKEVEN_DELTAS', 'BREAKEVEN_L', 'ANCILLA_FACTOR']),
                           ('研究5_validation.ipynb', ['QUICK', 'SEED', 'V3_CASES', 'V4_CASES', 'V5_CASES'])):
            cells = code_cells(S5 / name)
            self.assertIn('pip install', cells[0])
            params = {t.id for n in ast.parse(cells[1]).body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
            self.assertTrue(set(must) <= params, f'{name}: セル 2 に無いパラメータ {set(must) - params}')
            # セル 3 以降は、セル 2 のパラメータを（トップレベルで）上書きしない
            for src in cells[2:]:
                body = '\n'.join(l for l in src.splitlines() if not l.startswith('%'))
                later = {t.id for n in ast.parse(body).body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
                self.assertFalse(later & params, f'{name}: セル 2 のパラメータを後のセルが上書きしている {later & params}')

    def test_library_is_embedded_unchanged(self):
        lib = (S5 / 'src' / 'hier_lib.py').read_text(encoding='utf-8').rstrip('\n')
        for name in ('研究5_main.ipynb', '研究5_validation.ipynb'):
            self.assertIn(lib, [c.rstrip('\n') for c in code_cells(S5 / name)], f'{name} のライブラリが src/hier_lib.py と違う')

    def test_notebooks_have_no_outputs_and_parse(self):
        for name in ('研究5_main.ipynb', '研究5_validation.ipynb'):
            nb = json.loads((S5 / name).read_text(encoding='utf-8'))
            for c in nb['cells']:
                if c['cell_type'] == 'code':
                    self.assertEqual(c['outputs'], [])
                    src = '\n'.join(l for l in ''.join(c['source']).splitlines() if not l.startswith('%'))
                    ast.parse(src)


class Study5Algebra(unittest.TestCase):
    def test_group_cochain_identities(self):
        for N in range(2, 7):
            for row in H.group_cochain_checks(N, max_points=200_000, seed=1):
                self.assertEqual(row['violations'], 0, row)

    def test_descent_identity_is_exact(self):
        rng = np.random.default_rng(0)
        for n in range(2, 7):
            P, _ = H._points(n - 1, n, 200_000, rng)
            par = np.zeros(P.shape, dtype=np.int64)
            for b in range(n - 1):
                par ^= (P >> b) & 1
            big = (P & 1) | (par << 1) | ((P >> 1) << 2)
            diff = 2 * H._alpha_points(big, 0) - H._delta_points(lambda X: H._alpha_points(X, 0), P)
            self.assertEqual(int(np.count_nonzero(diff)), 0)


class Study5Lattice(unittest.TestCase):
    CASES = [(2, (3,)), (3, (2, 2)), (3, (3, 2)), (4, (1, 1, 1)), (4, (2, 2, 1)), (5, (1, 1, 1, 1)), (5, (2, 1, 1, 1)), (6, (1,) * 5)]

    def test_one_logical_qubit_and_orientation(self):
        for N, L in self.CASES:
            lat = H.Lattice(N, L)
            self.assertTrue(lat.check_orientation())
            self.assertTrue(H.Sector(lat).check_columns())
            self.assertEqual(H.logical_dimension(lat)['k_logical'], 1, (N, L))

    def test_logical_gate_is_R_N(self):
        for N, L in self.CASES:
            r = H.Checker(H.Lattice(N, L), n_samples=24, seed=2).summary()
            self.assertEqual((r['square_violations'], r['commute_violations'], r['covariance_violations']), (0, 0, 0), (N, L))
            self.assertEqual(r['logical_phase_units'], H.expected_phase_units(N), (N, L))
            self.assertEqual(H.expected_phase_units(N), H.PI_UNIT >> (N - 1))

    def test_negative_controls_fail(self):
        for N, L in [(3, (2, 2)), (4, (2, 2, 1)), (5, (2, 1, 1, 1))]:
            lat = H.Lattice(N, L)
            variants = [dict(max_k=0), dict(drop=(lat.n - 1,)), dict(alternate=False)] + ([dict(dressing=False)] if N >= 4 else [])
            for kw in variants:
                r = H.Checker(lat, n_samples=24, seed=2, w_terms=H.W_terms(lat, **kw)).summary()
                self.assertFalse(r['covariance_violations'] == 0 and r['logical_phase_units'] == H.expected_phase_units(N), (N, L, kw))
            r = H.Checker(lat, n_samples=24, seed=2, use_V=False).summary()
            self.assertGreater(r['covariance_violations'], 0)
            r = H.Checker(lat, n_samples=24, seed=2, w_terms=H.W_terms(lat, dressing='plus')).summary()
            good = r['covariance_violations'] == 0 and r['logical_phase_units'] == H.expected_phase_units(N)
            self.assertEqual(good, N <= 4, (N, L, 'cup-1 を + で足した式'))


class Study5Protocol(unittest.TestCase):
    def test_protocol_outputs_R_N_plus(self):
        rng = np.random.default_rng(5)
        for N, L in [(2, (4,)), (3, (2, 2)), (4, (2, 1, 1)), (5, (1, 1, 1, 1))]:
            sim = H.StateSim(H.Lattice(N, L))
            M, leak, stab = sim.logical_matrix()
            self.assertLess(leak, 1e-9)
            self.assertAlmostEqual(float(np.angle(M[1, 1] / M[0, 0]) / np.pi), 1 / 2 ** (N - 1), places=9)
            for mode in ('fix_before_U', 'frame'):
                for _ in range(3):
                    r = sim.run_protocol(rng, mode)
                    self.assertAlmostEqual(r['fidelity'], 1.0, places=9)
                    self.assertLess(r['fidelity_to_plus'], 0.999)

    def test_protocol_negative_controls(self):
        rng = np.random.default_rng(6)
        sim = H.StateSim(H.Lattice(4, (2, 1, 1)))
        a = [sim.run_protocol(rng, skip_out_correction=True) for _ in range(30)]
        b = [sim.run_protocol(rng, charge_mode='none') for _ in range(30)]
        self.assertTrue(any(r['fidelity'] < 0.99 for r in a if r['n_correction_gates'] > 0))
        self.assertTrue(all(r['fidelity'] < 0.99 for r in b if r['n_charges'] > 0))

    def test_dense_implementation_agrees(self):
        rng = np.random.default_rng(7)
        for N, L in [(2, (4,)), (3, (1, 1))]:
            lat = H.Lattice(N, L)
            sec, ds = H.Sector(lat), H.DenseSim(lat)
            for _ in range(3):
                r = ds.run_protocol(rng)
                self.assertAlmostEqual(r['fidelity'], 1.0, places=9)
                self.assertLess(r['leak_after_U'], 1e-9)
                self.assertTrue(r['outcome_consistent'])
                self.assertEqual(r['n_valid_pauli'], 2 ** (sec.D - len(sec.special_bits)))

    @unittest.skipUnless(importlib.util.find_spec('scipy') is not None, 'scipy が無い')
    def test_distances(self):
        self.assertEqual({k: v for k, v in H.pauli_code_distances(H.Lattice(3, (2, 2))).items() if k in ('d_X', 'd_Z')}, dict(d_X=7, d_Z=2))
        self.assertEqual({k: v for k, v in H.pauli_code_distances(H.Lattice(4, (2, 2, 2))).items() if k in ('d_X', 'd_Z')}, dict(d_X=43, d_Z=2))

    def test_resource_counts(self):
        r = H.resource_row(H.Lattice(4, (2, 2, 2)))
        self.assertEqual((r['qubits'], r['qubits_pauli_code'], r['sector_dim_D'], r['switch_in_check_X_weight_max'],
                          r['switch_in_check_dressing_gates_max'], r['X_error_spread_max']), (302, 246, 44, 14, 6, 12))
        self.assertEqual([g['hierarchy_level'] for g in H.gate_inventory(H.Lattice(5, (1, 1, 1, 1)))], [5, 5, 5, 5])


if __name__ == '__main__':
    unittest.main()
