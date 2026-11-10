"""研究 4 のノートブックを組み立てる。
    python build_notebooks.py
入力：cells/*.py（このフォルダ）、seq_lib.py、研究 3 のノート（物理ライブラリをそのまま取り込む）、
      研究 3 の結果（results_v11/cost_comparison.csv, aggregated_counts.csv）、../results_pilot/study4_mc.csv（あれば）。
出力：../研究4_main.ipynb、../研究4_validation.ipynb
研究 3 の物理ライブラリは 1 文字も変えずに埋め込む（tests/test_study4.py が確認する）。"""
import json, os, io, hashlib
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S3 = os.path.join(os.path.dirname(ROOT), '3_魔法状態蒸留との比較')
LIB_CELLS = range(5, 36)          # 研究 3 のノートの共通ライブラリ・D4 ライブラリ・雑音付き D4 ライブラリ


def cell(kind, src):
    c = dict(cell_type=kind, metadata={}, source=src.rstrip('\n').splitlines(keepends=True))
    if kind == 'code':
        c.update(execution_count=None, outputs=[])
    return c


def md(s):
    return cell('markdown', s)


def code(name):
    return cell('code', open(os.path.join(HERE, 'cells', name), encoding='utf-8').read())


def study3_library():
    nb = json.load(open(os.path.join(S3, 'D4_noisy_simulation.ipynb'), encoding='utf-8'))
    out = [md('## 研究 3 のライブラリ（変更なし・読み飛ばしてよい）\n\n'
              '研究 3 の `D4_noisy_simulation.ipynb` の物理ライブラリ（格子、回路、雑音モデル、Pauli proxy 法、復号器、'
              '厳密な参照シミュレータ）を**そのまま**埋め込んだもの。関数とクラスの定義だけで、実行しても何も出力しない。'
              '研究 4 で新しく書いたコードはこの次の節にある。')]
    for i in LIB_CELLS:
        c = nb['cells'][i]
        out.append(cell(c['cell_type'], ''.join(c['source'])))
    return out


def reference_cell():
    cc = pd.read_csv(os.path.join(S3, 'results_v11', 'cost_comparison.csv'))
    keep = ['scenario', 'p', 'target', 'litinski_protocol', 'litinski_volume', 'kobayashi_status', 'kobayashi_d_low',
            'kobayashi_volume_low', 'ratio_kobayashi_low_over_litinski']
    s3 = cc[keep].to_csv(index=False)
    ag = pd.read_csv(os.path.join(S3, 'results_v11', 'aggregated_counts.csv'))
    ag = ag[(ag.window == 'noisy') & (ag.kappa0 == 1) & (ag.kappa_in == 1) & (ag.kappa_out == 1)]
    ref = ag[['scenario', 'd', 'p', 'shots', 'n_half', 'n_one', 'eps']].to_csv(index=False)
    pilot_path = os.path.join(ROOT, 'results_pilot', 'study4_mc.csv')
    pilot = open(pilot_path, encoding='utf-8').read() if os.path.exists(pilot_path) else ''
    sha = hashlib.sha256(open(os.path.join(S3, 'results_v11', 'cost_comparison.csv'), 'rb').read()).hexdigest()
    src = ('# ==================================================================================================\n'
           '# 参照データ（埋め込み）\n'
           '#   STUDY3 : 研究 3 の比較表（3_魔法状態蒸留との比較/results_v11/cost_comparison.csv の一部の列）\n'
           f'#            sha256 = {sha}\n'
           '#            kobayashi_d_low = データで棄却されない最小のサイズ、ratio = その体積 ÷ 蒸留工場の体積\n'
           '#   REF3   : 研究 3 の本番データの出力不忠実度（K=1 と同じ回路。比較の参考。停止規則が違うので推定には使わない）\n'
           '#   EMBED_PILOT_MC : この研究の試行計算（results_pilot/study4_mc.csv）。RUN_MODE = "analysis_only" で使う\n'
           '# ==================================================================================================\n'
           f'STUDY3 = pd.read_csv(io.StringIO({s3!r}))\n'
           f'REF3 = pd.read_csv(io.StringIO({ref!r}))\n'
           f'EMBED_PILOT_MC = {pilot!r}\n'
           "print(len(STUDY3), '条件（研究 3 の比較表）,', len(REF3), '点（研究 3 の出力不忠実度）,', "
           "'試行データ', 'あり' if EMBED_PILOT_MC else 'なし')\n")
    return cell('code', src)


def seq_lib_cell():
    return cell('code', open(os.path.join(HERE, 'seq_lib.py'), encoding='utf-8').read())


def notebook(cells):
    return dict(cells=cells, metadata=dict(kernelspec=dict(display_name='Python 3', language='python', name='python3'),
                                           language_info=dict(name='python'), colab=dict(provenance=[])),
                nbformat=4, nbformat_minor=5)


MAIN = [
    md(open(os.path.join(HERE, 'cells', 'md_main_title.md'), encoding='utf-8').read()),
    code('m01_install.py'),
    code('m02_params.py'),
    code('m03_setup.py'),
    *study3_library(),
    md('## 研究 4 のライブラリ：連続サイクルの code switching\n\n'
       '研究 3 のクラスを書き換えず、サブクラスとして K 回連続の回路・復号器・実験を定義する。'
       '`SeqSwitchingCircuit`（回路）、`SeqFluxDecoder`・`SeqChargeDecoder`（復号器）、`SeqExperiment`（1 ショットの実行）、'
       '`seq_counts`（体積の数え上げ）。K=1 は研究 3 と同一になる。'),
    seq_lib_cell(),
    md('## 参照データ'),
    reference_cell(),
    md('## 1. 自己検査'),
    code('m20_selfcheck.py'),
    md('## 2. モンテカルロ\n\n定義（次のセル）と実行（その次のセル）。途中で止めても、`RESUME = True` のまま同じセルを実行すれば続きから計算する。'),
    code('m40_mc.py'),
    cell('code', "if RUN_MODE != 'analysis_only':\n    run_monte_carlo(PLAN[RUN_MODE])\nelse:\n    print('analysis_only：モンテカルロは実行しません')"),
    md('## 3. 回路の規模と償却係数'),
    code('m30_counts.py'),
    md('## 4. 出力不忠実度の集計'),
    code('m50_summary.py'),
    md('## 5. 1 サイクルあたりの誤り（加法性の検査）'),
    code('m60_percycle.py'),
    md('## 6. 間の FSC ラウンドを短くした効果'),
    code('m62_gap.py'),
    md('## 7. 費用の比較'),
    code('m70_cost.py'),
    md('## 8. 判定の要約'),
    code('m72_verdict.py'),
    md('## 9. 図'),
    code('m80_figs.py'),
]

VALID = [
    md(open(os.path.join(HERE, 'cells', 'md_val_title.md'), encoding='utf-8').read()),
    code('m01_install.py'),
    code('v02_params.py'),
    code('v03_setup.py'),
    *study3_library(),
    md('## 研究 4 のライブラリ：連続サイクルの code switching（本体のノートと同一）'),
    seq_lib_cell(),
    md('## V1　K=1 は研究 3 と同一'),
    code('v10_regression.py'),
    md('## V2　雑音なしで誤り 0'),
    code('v20_noiseless.py'),
    md('## V3　真の非 Clifford 回路との照合'),
    code('v30_lockstep.py'),
    md('## V4　負の対照'),
    code('v40_negative.py'),
    md('## V5　その他の整合性'),
    code('v50_misc.py'),
    md('## 結果'),
    code('v90_summary.py'),
]

if __name__ == '__main__':
    for name, cells in (('研究4_main.ipynb', MAIN), ('研究4_validation.ipynb', VALID)):
        path = os.path.join(ROOT, name)
        json.dump(notebook(cells), open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('wrote', path, len(cells), 'cells')
