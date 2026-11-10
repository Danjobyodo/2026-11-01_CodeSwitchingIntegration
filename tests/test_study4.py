"""研究 4（連続 T ゲートでの code switching の償却）の回帰テスト。
    python -m unittest tests.test_study4 -v
stim / pymatching が無い環境では、ノートの構造の検査だけを行う。"""
import ast, importlib.util, json, unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
S4 = ROOT / '4_連続Tゲートでの償却'
S3 = ROOT / '3_魔法状態蒸留との比較'
HAVE_SIM = all(importlib.util.find_spec(m) is not None for m in ('stim', 'pymatching'))


def code_cells(path):
    return [''.join(c['source']) for c in json.loads(path.read_text(encoding='utf-8'))['cells'] if c['cell_type'] == 'code']


def definitions(path):
    out = {}
    for src in code_cells(path):
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                out[node.name] = ast.dump(node)
    return out


def load_library():
    """研究 4 の本体ノートから、ライブラリのセル（関数・クラスの定義）だけを実行して名前空間を返す。"""
    import stim, pymatching, pandas as pd
    ns = dict(np=np, stim=stim, pymatching=pymatching, pd=pd)
    exec('import os, io, json, math, itertools', ns)
    cells = code_cells(S4 / '研究4_main.ipynb')
    start = next(i for i, s in enumerate(cells) if s.startswith('"""common_lib'))
    stop = next(i for i, s in enumerate(cells) if 'class SeqExperiment' in s)
    for src in cells[start:stop + 1]:
        exec(compile(src, 'study4_library', 'exec'), ns)
    return ns


class Study4Structure(unittest.TestCase):
    def test_first_cell_installs_and_second_cell_holds_parameters(self):
        for name, must in (('研究4_main.ipynb', ['RUN_MODE', 'PLAN', 'K_LIST', 'GAP_LIST', 'WORKERS', 'OUT_DIR', 'TARGETS']),
                           ('研究4_validation.ipynb', ['QUICK', 'SEED', 'V3_CASES'])):
            cells = code_cells(S4 / name)
            self.assertIn('pip', cells[0]); self.assertIn('stim', cells[0])
            for key in must:
                self.assertRegex(cells[1], rf'(?m)^{key}\b', f'{name}: {key} がセル 2 に無い')
            params = {t.id for n in ast.parse(cells[1]).body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
            self.assertTrue(set(must) <= params)

    def test_study3_library_is_embedded_unchanged(self):
        old = definitions(S3 / 'D4_noisy_simulation.ipynb')
        for name in ('研究4_main.ipynb', '研究4_validation.ipynb'):
            new = definitions(S4 / name)
            for key in ('D4SwitchingCircuit', 'CompiledProtocol', 'FastShot', 'FluxDecoder', 'ChargeDecoder', 'D4Experiment',
                        'TrueSim', 'NoiseModel', 'D4Lattice', 'D4Protocol', 'dressing', 'lockstep_full'):
                self.assertEqual(old[key], new[key], f'{name}: {key}')

    def test_notebooks_match_sources(self):
        lib = (S4 / 'src' / 'seq_lib.py').read_text(encoding='utf-8').rstrip('\n')
        for name in ('研究4_main.ipynb', '研究4_validation.ipynb'):
            self.assertTrue(any(s.rstrip('\n') == lib for s in code_cells(S4 / name)), name)


@unittest.skipUnless(HAVE_SIM, 'stim / pymatching が無い')
class Study4Physics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = load_library()

    def test_single_cycle_equals_study3_shot_by_shot(self):
        ns = self.ns
        a = ns['D4Experiment'](3, 3, 3, 3, ns['NoiseModel'](2e-3, p_idle=0.0))
        b = ns['SeqExperiment'](3, 3, 3, 3, 3, 1, ns['NoiseModel'](2e-3, p_idle=0.0))
        ia, _ = a.run(200, np.random.default_rng(1)); ib, _ = b.run(200, np.random.default_rng(1))
        self.assertTrue(np.array_equal(ia, ib)); self.assertGreater((ia > 0).sum(), 0)

    def test_noiseless_sequences_have_no_error(self):
        ns = self.ns
        for d, K in [(2, 2), (3, 2), (3, 3), (3, 4)]:
            inf, _ = ns['SeqExperiment'](d, 1, d, 1, 1, K, ns['NoiseModel'](0.0)).run(8, np.random.default_rng(K))
            self.assertEqual(float(inf.max()), 0.0, (d, K))

    def test_proxy_equals_true_non_clifford_circuit(self):
        ns = self.ns
        rng = np.random.default_rng(7)
        for L, K, p, n in [(1, 3, 0.03, 4), (2, 2, 0.02, 3)]:
            ex = ns['SeqExperiment'](L, 1, 1, 1, 1, K, ns['NoiseModel'](p))
            for _ in range(n):
                self.assertTrue(ns['lockstep_full'](L, 1, 1, ns['NoiseModel'](p), rng, ex=ex)['agree'], (L, K))

    def test_volume_counts(self):
        ns = self.ns
        for d in (3, 5):
            c1 = ns['seq_counts'](d, 1)
            self.assertEqual(c1['volume_total'], 632 * d ** 3 + 454 * d ** 2 + 8 * d - 14)
            self.assertEqual(c1['time_steps'], 62 * d + 21)
            v = [ns['seq_counts'](d, K, Rgap=1)['volume_total'] for K in (1, 2, 3)]
            self.assertEqual(v[2] - v[1], v[1] - v[0])
            self.assertLess(v[1] - v[0], v[0])            # 1 サイクルの増分は 1 回の準備より小さい


if __name__ == '__main__':
    unittest.main()
