"""研究 5 のノートブックを組み立てる。
    python build_notebooks.py
入力：cells/*.py, cells/*.md（このフォルダ）、hier_lib.py、
      研究 3 の結果（../../3_魔法状態蒸留との比較/results_v13/cost_comparison.csv。損益分岐の見積もりに使う列だけ）
出力：../研究5_main.ipynb、../研究5_validation.ipynb（どちらも単独で動く。他のファイルを読み込まない）
"""
import hashlib
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S3 = os.path.join(os.path.dirname(ROOT), '3_魔法状態蒸留との比較', 'results_v13', 'cost_comparison.csv')


def cell(kind, src):
    c = dict(cell_type=kind, metadata={}, source=src.rstrip('\n').splitlines(keepends=True))
    if kind == 'code':
        c.update(execution_count=None, outputs=[])
    return c


def md(s):
    return cell('markdown', s)


def read(name):
    return open(os.path.join(HERE, 'cells', name), encoding='utf-8').read()


def code(name):
    return cell('code', read(name))


def lib_cell():
    return cell('code', open(os.path.join(HERE, 'hier_lib.py'), encoding='utf-8').read())


def reference_cell():
    cc = pd.read_csv(S3)
    keep = ['scenario', 'p', 'target', 'litinski_protocol', 'litinski_qubits', 'litinski_volume']
    sha = hashlib.sha256(open(S3, 'rb').read()).hexdigest()
    src = ('# ==================================================================================================\n'
           '# 参照データ（埋め込み）：研究 3 の比較表のうち、15-to-1 蒸留の工場の量子ビット数と体積\n'
           '#   出所 3_魔法状態蒸留との比較/results_v13/cost_comparison.csv\n'
           f'#   sha256 = {sha}\n'
           '#   target = T 1 個の要求誤り、litinski_volume = 量子ビット × ステップ（研究 3 と同じ単位）\n'
           '# ==================================================================================================\n'
           f'STUDY3 = pd.read_csv(io.StringIO({cc[keep].to_csv(index=False)!r}))\n'
           "print(len(STUDY3), '行（研究 3 の蒸留の表）')\n")
    return cell('code', src)


def notebook(cells):
    for i, c in enumerate(cells):
        c['id'] = f'cell-{i:02d}'
    return dict(cells=cells, metadata=dict(kernelspec=dict(display_name='Python 3', language='python', name='python3'),
                                           language_info=dict(name='python'), colab=dict(provenance=[])),
                nbformat=4, nbformat_minor=5)


LIB_MD = ('## ライブラリ（読み飛ばしてよい）\n\n'
          '格子（`Lattice`）、位相多項式（`stabilizer_terms`, `W_terms`）、配位の空間（`Sector`）、恒等式の検査（`Checker`）、'
          '状態ベクトルでのプロトコル（`StateSim`）、独立な実装（`DenseSim`）、距離と資源（`pauli_code_distances`, `resource_row`）、'
          '群コチェインの検査（`group_cochain_checks`）。関数とクラスの定義だけで、実行しても何も出力しない。'
          '`src/hier_lib.py` と同一。')

MAIN = [
    md(read('md_main_title.md')),
    code('m01_install.py'),
    code('m02_params.py'),
    code('m03_setup.py'),
    md(LIB_MD),
    lib_cell(),
    md('## 参照データ'),
    reference_cell(),
    md('## 1. 符号と論理ゲートの検査（任意の大きさ）'),
    code('m10_identity.py'),
    md('## 2. code switching の厳密な実行（状態ベクトル）'),
    code('m20_protocol.py'),
    md('## 3. 資源の数え上げ'),
    code('m30_resources.py'),
    md('## 4. 各操作の Clifford 階層'),
    code('m40_levels.py'),
    md('## 5. 損益分岐の見積もり（$\\sqrt T$。雑音のシミュレーションではない）'),
    code('m50_breakeven.py'),
    md('## 6. 図'),
    code('m60_figs.py'),
    md('## 7. まとめ'),
    code('m70_verdict.py'),
]

VAL = [
    md(read('md_val_title.md')),
    code('m01_install.py'),
    code('v02_params.py'),
    code('v03_setup.py'),
    md(LIB_MD),
    lib_cell(),
    md('## V1. 群コチェインの恒等式'),
    code('v10_cochain.py'),
    md('## V2. [KZH] の式との一致、格子の向き、配位空間'),
    code('v20_kzh.py'),
    md('## V3. 負の対照（式）'),
    code('v30_negative.py'),
    md('## V4. 負の対照（プロトコル）'),
    code('v40_protocol_negative.py'),
    md('## V5. 独立な実装との一致'),
    code('v50_dense.py'),
    md('## V6. 再現性'),
    code('v60_repro.py'),
    md('## まとめ'),
    code('v90_summary.py'),
]

if __name__ == '__main__':
    for name, cells in (('研究5_main.ipynb', MAIN), ('研究5_validation.ipynb', VAL)):
        path = os.path.join(ROOT, name)
        json.dump(notebook(cells), open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('wrote', path, len(cells), 'cells')
