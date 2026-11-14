"""Build standalone v13 notebooks (analysis of v9.2 + v10 decision family + v11 table-wide lower bound; v13: figures drawn
from the result CSVs by figures_v13.py), preserving the v9 physical libraries verbatim.

The versioned v9 notebooks are an intentional, retained input. Only analysis and
presentation are replaced (v13 changes presentation only: the numbers of the result CSVs are those of v12); outputs are cleared. No files outside this folder are written.
Usage (in this folder): python build_notebooks_v13.py   -- a few seconds (no simulation).
"""
from pathlib import Path
import hashlib,json,ast
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'旧版'/'3_魔法状態蒸留との比較_v9'   # v9 physics libraries, kept verbatim
def set_source(cell,text): cell['source']=text.splitlines(keepends=True)
def code(text):return dict(cell_type='code',execution_count=None,metadata={},outputs=[],source=text.splitlines(keepends=True))
def markdown(text):return dict(cell_type='markdown',metadata={},source=text.splitlines(keepends=True))
COMMON = ('方法（物理回路・雑音・復号器・統計・判定）は論文の研究 3 の節。出力先は results_v13 / figures_v13。'
          'ファイルの一覧と読み方は同フォルダの README.md「出力ファイル」。変更履歴はリポジトリの CHANGELOG.md。\n'
          'コードの引数 `L`（`D4Lattice(L)`, `D4Protocol(L)`, `D4Experiment(L, ...)` など）は、論文の平面パッチの符号距離 $d$（1 辺のプラケット数）と同じ。\n')
HEADERS = {
 'noisy_cost_comparison.ipynb': '# 研究 3：Kobayashi 方式と 15-to-1 蒸留の比較 — v13（2026-11-13）\n\n' + COMMON + """
**Colab での所要時間の目安：CPU で約 30 分**（既定 `DATA_MODE='reference'`、`N_BOOT=200`。大半はモデルのブートストラップ。`N_BOOT=20` なら数分）。新しいモンテカルロはしない。

**出力**（9 ファイル）：`results_v13/` に `aggregated_counts.csv`（点ごとの集計）、`data_intervals.csv`（点ごとのデータの区間）、`model_predictions.csv`（モデルの予測）、`model_curves.csv`（図の曲線の元データ）、`fit_diagnostics.json`（当てはめの記録）、`factory_candidates.csv`（蒸留側の候補 1,632 × 10 条件）、`cost_comparison.csv`（**比較の表。主な結果**）。`figures_v13/` に `d4_logical_error.png`（出力誤りとモデル）、`cost_comparison.png`（出力誤り vs 体積）。図は最後のセルが上の CSV から描く（`figures_v13.py`。CSV があれば `python figures_v13.py` だけで数秒で描き直せる）。
""",
 'D4_noisy_simulation.ipynb': '# 研究 3：Kobayashi 方式の雑音付きモンテカルロと表面符号の較正 — v13（2026-11-13）\n\n' + COMMON + """
**Colab での所要時間の目安**（本番データの記録 `seconds` から。1 ショットあたり B で $d=3,5,7,9$ がそれぞれ約 2.5, 9, 31, 108 ms、A は約 1.3〜2 倍）

| 実行するもの | 目安 |
|---|---|
| `QUICK=True`（既定。動作確認、2 点 × 2 サイズ × 400 ショット＋小さい較正） | 約 1〜2 分（この環境の実測 41 秒） |
| `QUICK=False`, `RUN='all'`（全 78 点 × 10⁵ ショット＋較正） | CPU 約 80〜90 時間分（Colab の 2 コアで 2 日程度）。本番データは `data/` にあるので通常は不要 |
| `QUICK=False`, `RUN='extend'`、1 点に 10⁶ ショット追加（例 B・$p=2\\times10^{-4}$・$d=7$） | CPU 約 9 時間分（2 コアで約 4〜5 時間） |

**出力**：`results_v13/d4_noisy_mc.csv`（チャンクごとの MC の記録。`QUICK=True` では `_quick` 付き）、`results_v13/surface_code_plog.csv`（表面符号の較正）、追記した場合は `results_v13/d4_noisy_mc_runs.jsonl`（追加実行の停止規則の記録）。図はノートの中に表示するだけで保存しない。
""",
 'validation.ipynb': '# 研究 3：物理の検証 — v13（2026-11-13）\n\n' + COMMON + """
**Colab での所要時間の目安：CPU で約 2 時間**（既定 `QUICK=False`。`QUICK=True` では約 30〜45 分（この環境の実測 29 分、179 PASS・0 FAIL・3 INFO）。`FULL_KL=True` にすると $L=6$ の距離の証明が加わり、さらに大きく増える）。物理コードを変えたときだけ実行する。

**出力**：`results_v13/validation.json`（検査項目ごとの PASS／FAIL／INFO と、検証していない事項の一覧）。最後に `<PASS 数> PASS, <FAIL 数> FAIL, <INFO 数> INFO` を表示する。
""",
}


# ---------------------------------------------------------------------------------------------------------------
# Publication cleanup (v13): the v9 notebooks are kept verbatim as the input; only the following edits are applied.
#  * PUB_COMMENT: comments / docstrings only (internal references, version tags).  Each edited cell is checked to have
#    the same abstract syntax tree (docstrings removed) as before, i.e. no code is changed.
#  * PUB_CODE: removal of unused parameters and local variables (no side effects; the outputs were checked to be
#    identical before and after).
#  * PUB_MARKDOWN: explanatory text.
#  Every pattern must be found at least once over the three notebooks (stale patterns fail the build).
PUB_COMMENT = [
 ('(protocol step 5 of the noiseless check V7)', '(protocol step 5 of the noiseless check V7 in validation.ipynb)'),
 ('validated in V7/V7b/V8).', 'validated in validation.ipynb V7, V7b, V8).'),
 ('version (every detector set located in the DEM, the last round included) was tested in v6 and made\n        the decoder WORSE (single-fault first-order coefficient at d = 3, scenario B: 4.2 -> 8.0; the\n        attribution change alone is neutral): nearly free erased edges also open cheap wrong paths when the\n        flux attribution is wrong.  See docs/methods.md sec. 12."""',
  'version (every detector set located in the DEM, the last round included) was tested during development\n        and made the decoder WORSE (single-fault first-order coefficient at d = 3, scenario B: 4.2 -> 8.0; the\n        attribution change alone is neutral): nearly free erased edges also open cheap wrong paths when the\n        flux attribution is wrong."""'),
 ('decoders fail to correct are located (validation N5).', 'decoders fail to correct are located (validation.ipynb N5).'),
 ("""    sampled ones.  only_window: restrict to the faults in the switching window (ex.window).""",
  """    sampled ones.  only_window: restrict to the faults in the switching window (ex.window).
    The dynamic faults ('SOCZ', i, j) act only in the shots in which that physical switch-out CZ is applied (about
    half of the branches, depending on the outcomes a_dec); with their weight 1/15 per Pauli, the mean over the seeds
    is an unbiased estimate of their contribution, but with seeds=2 its variance is large."""),
 ("ek, src = row.s / row.shots, 'data'             # simulated d: the measured value (v6)", "ek, src = row.s / row.shots, 'data'             # simulated d: the measured value"),
]
PUB_CODE = [
 ('    def __init__(self, comp, dem_noise=None, aligned=True):\n', '    def __init__(self, comp, aligned=True):\n'),
 ('        nz = dem_noise or comp.noise\n', ''),
 ('self._dem_circuit(nz)', 'self._dem_circuit()'),
 ('    def _dem_circuit(self, nz):\n', '    def _dem_circuit(self):\n'),
 ("            noiseless = blk['name'][0] == 'FIN'\n", ''),
 ('                touched = {q for op in cm.ops for q in op[1:]}\n', ''),
 ("            lines.append('TICK')\n        n = circ.nq\n", "            lines.append('TICK')\n"),
 ('    reason of the enumeration (see low_weight_stabilizer_shifts).  t = 0 is covered by d_Z."""\n    lat = cd.lat\n',
  '    reason of the enumeration (see low_weight_stabilizer_shifts).  t = 0 is covered by d_Z."""\n'),
 ("                code = self.comp.blocks[f['block']]['code'] or 'D4'\n", ''),
 ('                rowset = {lab for lab, _ in rows}\n', ''),
 ('    rows_eq = []                          # for each generator: commutator linear part as function of c\n', ''),
 ('    A_cols, b_vec = [], None\n', '    A_cols = []\n'),
 ('    P, c, fsc = circ.P, circ.c, circ.P.fsc\n', '    c, fsc = circ.c, circ.P.fsc\n'),
 ("    sx = lambda c0, c: ('store', [c0] + [c] * 4, [0] * 5)\n", ''),
 ('    t_used = float(prev.seconds.sum()) if prev is not None else 0.0\n', ''),
 ('    t_start = time.time()\n    while n_total < n_target:', '    while n_total < n_target:'),
 ('    rows = []\n    t0 = time.time()\n    for scen, f in SCENARIOS.items():', '    rows = []\n    for scen, f in SCENARIOS.items():'),
]
PUB_MARKDOWN = [
 ('* `LOWP_QUIET_POINTS`（v6）：', '* `LOWP_QUIET_POINTS`：'),
 ('* `RUN`（v6）：', '* `RUN`：'),
 ('# 第 1 部 D4 符号と code switching（雑音なし、v4 から引き継ぎ）', '# 第 1 部 D4 符号と code switching（雑音なし）'),
 ('# 第 2 部 15-to-1 と GoSC の配置（雑音なし、v4 から引き継ぎ）', '# 第 2 部 15-to-1 と GoSC の配置（雑音なし）'),
 ('# 第 3 部 雑音付きシミュレーションの検証（v5）', '# 第 3 部 雑音付きシミュレーションの検証'),
]
PUB_USED = {}

def _same_code(a, b):
    def tree(src):
        src = '\n'.join('pass' if l.lstrip().startswith(('!', '%')) else l for l in src.splitlines())
        t = ast.parse(src)
        for node in ast.walk(t):
            body = getattr(node, 'body', None)
            if isinstance(body, list):
                node.body = [n for n in body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, 'value', None), ast.Constant)
                                                     and isinstance(n.value.value, str))] or [ast.Pass()]
        return ast.dump(t)
    return tree(a) == tree(b)

def publication_cleanup(nb, filename):
    for cell in nb['cells']:
        text = ''.join(cell['source'])
        if cell['cell_type'] == 'markdown':
            for old, new in PUB_MARKDOWN:
                if old in text:
                    text = text.replace(old, new); PUB_USED[old] = PUB_USED.get(old, 0) + 1
        elif cell['cell_type'] == 'code' and 'EMBED_MC =' not in text:
            for old, new in PUB_COMMENT:
                if old in text:
                    new_text = text.replace(old, new)
                    assert _same_code(text, new_text), (filename, old[:60])
                    text = new_text; PUB_USED[old] = PUB_USED.get(old, 0) + 1
            for old, new in PUB_CODE:
                if old in text:
                    text = text.replace(old, new); PUB_USED[old] = PUB_USED.get(old, 0) + 1
        set_source(cell, text)


def build():
    module=(ROOT/'analysis_v13.py').read_text()
    figures_module=(ROOT/'figures_v13.py').read_text()
    def embed_module(name,text):
        # the notebooks are standalone on Colab: a module is embedded as source and registered under its name
        return (f'_{name}=types.ModuleType("{name}")\nsys.modules["{name}"]=_{name}\n'
                f'exec(compile({text!r},"{name}.py","exec"),_{name}.__dict__)\n')
    for filename in ['noisy_cost_comparison.ipynb','D4_noisy_simulation.ipynb','validation.ipynb']:
        nb=json.loads((SOURCE/filename).read_text())
        for cell in nb['cells']:
            if cell['cell_type']=='code': cell['outputs']=[];cell['execution_count']=None
        set_source(nb['cells'][0], HEADERS[filename])
        text=''.join(nb['cells'][1]['source']).replace("RESULTS, FIGURES = 'results', 'figures'","RESULTS, FIGURES = 'results_v13', 'figures_v13'")
        set_source(nb['cells'][1],text)
        if filename=='noisy_cost_comparison.ipynb':
            # Canonical reference CSVs and full hashes replace stale legacy results.
            c44=''.join(nb['cells'][44]['source'])
            tree=ast.parse(c44)
            for var,file in [('EMBED_MC','d4_noisy_mc.csv'),('EMBED_CAL','surface_code_plog.csv')]:
                val=(ROOT/'data'/file).read_text()
                node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==var for t in n.targets))
                lines=c44.splitlines(keepends=True)
                # Node coordinates remain valid until the next replacement; reparse below.
                lines[node.lineno-1:node.end_lineno]=[f'{var} = {val!r}\n']
                c44=''.join(lines);tree=ast.parse(c44)
            c44=c44.replace("hashlib.sha256(t.encode()).hexdigest()[:16]","hashlib.sha256(t.encode()).hexdigest()")
            start=c44.index('REF_SHA =');end=c44.index('\nsha =',start)
            hashes={k:hashlib.sha256((ROOT/'data'/f).read_bytes()).hexdigest() for k,f in [('mc','d4_noisy_mc.csv'),('cal','surface_code_plog.csv')]}
            c44=c44[:start]+'REF_SHA = '+repr(hashes)+c44[end:]
            c44 += '\nPROV.update(analysis_version="v13", source_commit="e581ca550bdcaf9c59177e41ae92dcc5786f2ba7", analysis_sha256='+repr(hashlib.sha256(module.encode()).hexdigest())+')\n'
            set_source(nb['cells'][44],c44)
            set_source(nb['cells'][48],'''import analysis_v13 as stats
g=stats.aggregate_counts(mc)
g['eps_over_p']=g.eps/g.p
k1=(g.kappa0==1)&(g.kappa_in==1)&(g.kappa_out==1)
main=g[k1&(g.window=='noisy')].copy()
quiet=g[k1&(g.window=='quiet')].copy()
g.to_csv(f'{RESULTS}/aggregated_counts{OUT_SUFFIX}.csv',index=False)
print('Validated categorical chunks; full counts retained.')
''')
            set_source(nb['cells'][50],(ROOT/'cells/fit_models.py').read_text())
            factories=''.join(nb['cells'][56]['source'])
            factories += "\npd.concat([df.assign(scenario=sc,p=pp) for (sc,pp),df in LIT.items()],ignore_index=True).to_csv(f'{RESULTS}/factory_candidates{OUT_SUFFIX}.csv',index=False)\n"
            set_source(nb['cells'][56],factories)

            set_source(nb['cells'][49],'''## 多項分布による記述モデル
各点を (n_zero,n_half,n_one) の多項分布として当てはめ、再標本化も多項分布で行う。
quiet の2カテゴリ強度は log-linear、noisy はそれに窓の強度を加え、zero基準のsoftmaxで確率化する。
main はd>=7、感度W5/altWはd>=5。
全最適化の成功・境界・反復を保存する。bootstrap範囲はモデル条件付きで、有限標本保証ではない。
''')
            set_source(nb['cells'][59],'''## データによる到達保証とモデル予測
独立ショットの不忠実度 X∈[0,1] に対するBeta混合confidence sequence（旧MCの失敗数・時間による停止と後からの追加にも有効）を用いる。
主判定の族は「その判定（シナリオ・p・窓）で候補になるシミュレーション済みの d 全て」：選んだ d と「最小サイズの確定」を
全ての要求値について同時に95%で保護する。表全体（最大200点）の同時保証は、より厳しい感度の列 `*_tablewide_*` に残す。固定Nの参考区間は別列。
実測点が未確定ならモデルで上書きしない。モデル支持（bootstrap>=95%）は別列で、データ保証ではない。
小さいサイズが未確定なら、保証された候補があっても最小費用確定とはしない。
Litinski列は文献誤り予算の中央値であり、両方式に同じ統計保証があるという比較ではない。
''')
            set_source(nb['cells'][60],(ROOT/'cells/decisions.py').read_text())
            # v13: stale explanations inherited from v9 (paths, the 16-digit hash, the v6 conclusion) are replaced.
            def patch_markdown(index,pairs):
                text=''.join(nb['cells'][index]['source'])
                for old,new in pairs:
                    assert text.count(old)==1,(index,old)
                    text=text.replace(old,new)
                set_source(nb['cells'][index],text)
            patch_markdown(43,[("（リポジトリの `results/` と同一。下の SHA-256 で照合できる）","（リポジトリの `data/` の 2 つの CSV と同一。下の SHA-256 で照合できる）"),
                ("`QUICK = False` で実行して得た `results/d4_noisy_mc.csv`, `results/surface_code_plog.csv`","`QUICK = False` で実行して得た `results_v13/d4_noisy_mc.csv`, `results_v13/surface_code_plog.csv`"),
                ("`QUICK = True` の動作確認の結果 `results/*_quick.csv`","`QUICK = True` の動作確認の結果 `results_v13/*_quick.csv`"),
                ("シミュレーションのノートで作られた `results/` の 2 つの CSV を、このノートのランタイムの `results/` に","シミュレーションのノートで作られた `results_v13/` の 2 つの CSV を、このノートのランタイムの `results_v13/` に"),
                ("入力の SHA-256（先頭 16 桁）","入力の SHA-256")])
            patch_markdown(53,[("：`docs/methods.md` §4.1）","）")])
            set_source(nb['cells'][57],'''## 第IV部 比較
蒸留側は候補の中のパレート前線（体積を増やしても出力誤りが下がらない候補を除いたもの）、code switching 側は $d=3,\\dots,9$ のシミュレーションと II-2 のモデル。図は最後の第V部で、保存した CSV から描く。
''')
            set_source(nb['cells'][61],'''### IV-3. code switching が同じ体積に収まるために必要な改善（診断値）
要求誤りごとに、蒸留の最小体積以下に収まる code switching の最大のサイズ $d_{\\max}$ を求め、そこでの $\\varepsilon_K(d_{\\max},p)$（シミュレーションした $d$ では測定値、それより大きい $d$ ではモデル：`basis`）が要求誤りの何倍か（`required_improvement`）を示す。**現在の費用モデルを固定した場合の目安**で、復号器やスケジュールを変えれば量子ビット数・時間も変わるので、この倍率の改善で必ず同じ費用に並ぶという保証ではない。このセルが比較の表 `cost_comparison.csv` を保存する。
''')
            set_source(nb['cells'][63],'''## 第V部 図
次のセルは、図の曲線の元データ `model_curves.csv` を保存してから、`figures_v13.py` で 2 枚の図を描く。図に出る数値は全て上で保存した CSV（`data_intervals`・`model_curves`・`factory_candidates`・`cost_comparison`）の値で、このセルでは当てはめも判定もしない。

* `d4_logical_error.png`：出力誤り $\\varepsilon_K(d,p)$。上の段＝本来のシミュレーション、下の段＝切り替えの窓を雑音なしにした診断。マーカー＝データ、縦棒＝判定に使う 95% の信頼列の区間（その $p$ の候補サイズ全体で同時）、白抜きの下向き三角＝失敗 0 の点（区間の上端）、曲線＝当てはめたモデル。同じ $p$ のマーカーは重ならないよう横に少しずらして描く。
* `cost_comparison.png`：出力誤り vs 時空間体積。橙の階段＝蒸留（候補のパレート前線）、青の丸＝code switching のシミュレーション（$d$ を添える）、青の破線＝そのモデルの $d>9$ への外挿、灰色の破線＝窓を雑音なしにした診断のモデル（**限界ではなく**「窓の誤りが無かったら」）。各パネルの題の下に、要求 $10^{-4}$ についての比較の表の結果を書く。

**読み方**：データによる保証（`data_certified`）・モデルによる支持・未確定を区別する。データによる下限（`*_low_*`）とモデルによる外挿を混同しない。蒸留側は文献の誤り予算の中央値で、同じ統計保証は無い。
''')
            nb['cells'].append(code((ROOT/'cells/figures.py').read_text()))
            # v13: the two figure cells of v9 are removed (the figures are drawn by the last cell)
            for old_figure in (nb['cells'][58],nb['cells'][52]):
                assert old_figure['cell_type']=='code' and 'plt.savefig' in ''.join(old_figure['source'])
                nb['cells'].remove(old_figure)
            embed='import types, sys\n'+embed_module('analysis_v13',module)+embed_module('figures_v13',figures_module)
            nb['cells'].insert(44,code(embed))
        else:
            if filename=='D4_noisy_simulation.ipynb':
                cfg=''.join(nb['cells'][43]['source'])
                cfg=cfg.replace('TIME_CAP, MAX_FAIL, WORKERS = 1200, 200, 4','WORKERS = 4').replace('TIME_CAP, MAX_FAIL, WORKERS = 60, 50, 2','WORKERS = 2').replace(', max_fail=100, time_cap=TIME_CAP // 2','').replace(', max_fail=100','').replace('EXTEND_SECONDS = 3600','')
                cfg += '\n# fixed sample sizes; no failure-count or wall-clock stopping.\nSHOTS_PER_POINT = 400 if QUICK else 100000\nEXTEND_SHOTS = 100000\n'
                set_source(nb['cells'][43],cfg)
                run=''.join(nb['cells'][47]['source'])
                run=run.replace('    os.remove(MC_CSV)', '    raise FileExistsError("Existing CSV: set RESUME=True or choose a new output directory")')
                run=run.replace("    t_start = time.time()\n    cap, fmax", "    n_previous = int(prev.shots.sum()) if prev is not None else 0\n    n_total = n_previous\n    n_target = n_previous + EXTEND_SHOTS if pt.get('extend') else SHOTS_PER_POINT\n    t_start = time.time()\n    cap, fmax")
                run=run.replace('while t_used + time.time() - t_start < cap and nf < fmax:', 'while n_total < n_target:')
                run=run.replace('ex.run(chunk, np.random.default_rng(seed))', 'ex.run(min(chunk, n_target-n_total), np.random.default_rng(seed))')
                run=run.replace('shots=chunk, sum_infidelity=', "shots=len(inf), stopping_rule='fixed_shots', sum_infidelity=")
                begin=run.index("    cap, fmax =")
                end=run.index("    while n_total",begin)
                run=run[:begin]+run[end:]
                run=run.replace('EXTEND_SECONDS','EXTEND_SHOTS').replace("'s each; new points:'","'shots each; new points:'")
                run=run.replace('        k += 1', '        n_total += len(inf)\n        k += 1')
                # v11: the stored production CSV (adaptive-stopping format) has no stopping_rule column. Appending a row
                # with that extra column made the file unreadable (22 header fields, 23 in the new rows). New rows are
                # written in the columns of the existing file; the stopping rule of the run is recorded in a side file.
                old_done="done = pd.read_csv(MC_CSV) if os.path.exists(MC_CSV) else None\n"
                assert run.count(old_done)==1
                run=run.replace(old_done, old_done+"MC_COLUMNS = list(done.columns) if done is not None else None   # append in the columns of the existing file\n"
                    "if MC_COLUMNS is not None and 'stopping_rule' not in MC_COLUMNS:\n"
                    "    import json as _json\n"
                    "    print('existing CSV has no stopping_rule column: new chunks are appended in its columns; run', RUN_ID, 'uses fixed shot numbers')\n"
                    "    with open(os.path.splitext(MC_CSV)[0] + '_runs.jsonl', 'a') as _f:\n"
                    "        _f.write(_json.dumps(dict(run_id=RUN_ID, stopping_rule='fixed_shots', run=RUN, shots_per_point=SHOTS_PER_POINT, extend_shots=EXTEND_SHOTS)) + '\\n')\n")
                old_write="            pd.DataFrame([row]).to_csv(MC_CSV, mode='a', header=new, index=False)\n"
                assert run.count(old_write)==1
                run=run.replace(old_write, "            _cols = globals().get('MC_COLUMNS')\n"
                    "            _frame = pd.DataFrame([row])\n"
                    "            if _cols is not None and not new:\n"
                    "                _frame = _frame.reindex(columns=_cols)   # same columns as the existing file\n"
                    "            _frame.to_csv(MC_CSV, mode='a', header=new, index=False)\n")
                set_source(nb['cells'][47],run)
                calibration=''.join(nb['cells'][49]['source'])
                calibration=calibration.replace('def calibrate():\n', 'def calibrate():\n    if os.path.exists(CAL_CSV):\n        print("Reusing existing calibration CSV (choose a new output directory to recalibrate):", CAL_CSV)\n        return pd.read_csv(CAL_CSV)\n')
                set_source(nb['cells'][49],calibration)

            if filename=='validation.ipynb':
                # v12: with QUICK=True only 40 branches are sampled at L=2, and requiring all 2^4 = 16 outcome patterns
                # to occur fails by chance most of the time (expected number of missing patterns 16*(15/16)^40 ~ 1.2).
                # QUICK runs keep the chi^2 test only; the full run (200 branches, miss probability ~4e-5) is unchanged.
                old_crit="       len(cm) == 2 ** ng and p_m > 1e-3, dict(sorted(cm.items())))"
                hits=[c for c in nb['cells'] if c['cell_type']=='code' and old_crit in ''.join(c['source'])]
                assert len(hits)==1
                set_source(hits[0],''.join(hits[0]['source']).replace(old_crit,
                    "       (len(cm) == 2 ** ng or QUICK) and p_m > 1e-3, dict(sorted(cm.items())))  # QUICK keeps the chi^2 test only"))
            # No new physics: old physical validation remains applicable.
            nb['cells'].insert(1,markdown('物理回路・雑音・復号のコードは `validation.ipynb` で検証したもの（検証していない事項は `validation.ipynb` の最後に記載）。\n'
                                          if filename=='D4_noisy_simulation.ipynb' else '検証していない事項は、このノートの最後に記載する。\n'))
        publication_cleanup(nb, filename)
        (ROOT/filename).write_text(json.dumps(nb,ensure_ascii=False,indent=1))
    stats_embed='import types, sys\n'+embed_module('analysis_v13',module)
    stats=dict(nbformat=4,nbformat_minor=0,metadata=dict(kernelspec=dict(display_name='Python 3',name='python3'),language_info=dict(name='python')),
        cells=[markdown('# 研究 3：統計手法の検証 — v13（CPU、単独 Colab ノート）\n\n固定Nの厳密な分布列挙、逐次停止時のconfidence sequence、カテゴリ再標本化を検査する。物理検証とは別。\n\n**Colab での所要時間の目安：CPU で 1 分以内（この環境の実測 2 秒）。** **出力**：`results_v13/statistics_validation.json`（検査項目ごとの合否）。最後に `STATISTICS VALIDATION PASSED`。\n'),
               code(stats_embed),code((ROOT/'cells/statistics_validation.py').read_text())])
    (ROOT/'statistics_validation_v13.ipynb').write_text(json.dumps(stats,ensure_ascii=False,indent=1))

if __name__=='__main__':
    build()
    missing=[old[:60] for old,_ in PUB_COMMENT+PUB_CODE+PUB_MARKDOWN if not PUB_USED.get(old)]
    assert not missing, ('publication patterns not found', missing)
