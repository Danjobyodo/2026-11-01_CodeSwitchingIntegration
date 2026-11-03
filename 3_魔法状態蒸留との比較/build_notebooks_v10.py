"""Build standalone v10 notebooks (analysis of v9.2 + v10 decision family), preserving the v9 physical libraries verbatim.

The versioned v9 notebooks are an intentional, retained input. Only analysis and
presentation are replaced; outputs are cleared. No files outside this folder are written.
"""
from pathlib import Path
import hashlib,json,ast
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'旧版'/'3_魔法状態蒸留との比較_v9'   # v9 physics libraries, kept verbatim
def set_source(cell,text): cell['source']=text.splitlines(keepends=True)
def code(text):return dict(cell_type='code',execution_count=None,metadata={},outputs=[],source=text.splitlines(keepends=True))
def markdown(text):return dict(cell_type='markdown',metadata={},source=text.splitlines(keepends=True))
def build():
    module=(ROOT/'analysis_v10.py').read_text()
    for filename in ['noisy_cost_comparison.ipynb','D4_noisy_simulation.ipynb','validation.ipynb']:
        nb=json.loads((SOURCE/filename).read_text())
        for cell in nb['cells']:
            if cell['cell_type']=='code': cell['outputs']=[];cell['execution_count']=None
        set_source(nb['cells'][0], '# v10（2026-11-03、完成版）\n\n物理回路は v9 と同じ。出力先は results_v10 / figures_v10。\n'
             '統計は0・1/2・1の多項分布。データ保証とモデル予測は別。旧版の比較結論は引き継がない。\n'
             '詳細と実行順は同フォルダ README.md と ../論文草稿/ の方法の節を参照。\n')
        text=''.join(nb['cells'][1]['source']).replace("RESULTS, FIGURES = 'results', 'figures'","RESULTS, FIGURES = 'results_v10', 'figures_v10'")
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
            c44 += '\nPROV.update(analysis_version="v10", source_commit="e581ca550bdcaf9c59177e41ae92dcc5786f2ba7", analysis_sha256='+repr(hashlib.sha256(module.encode()).hexdigest())+')\n'
            set_source(nb['cells'][44],c44)
            set_source(nb['cells'][48],'''import analysis_v10 as a10
g=a10.aggregate_counts(mc)
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

            set_source(nb['cells'][49],'''## 多項分布による記述モデル（v9.2 で導入、v10 も同じ）
各点を (n_zero,n_half,n_one) の多項分布として当てはめ、再標本化も多項分布で行う。
quiet の2カテゴリ強度は log-linear、noisy はそれに窓の強度を加え、zero基準のsoftmaxで確率化する。
これは v9 の平均モデルからの変更。main はd>=7、感度W5/altWはd>=5。
全最適化の成功・境界・反復を保存する。bootstrap範囲はモデル条件付きで、有限標本保証ではない。
''')
            s=''.join(nb['cells'][52]['source']).replace("3 / zero.shots","[a10.bounded_mean_ci(r)[1] for _,r in zero.iterrows()]").replace('3/shots','95% bounded-loss upper bound')
            set_source(nb['cells'][52],s)
            set_source(nb['cells'][59],'''## データによる到達保証とモデル予測（v10）
独立ショットの不忠実度 X∈[0,1] に対するBeta混合confidence sequence（旧MCの失敗数・時間による停止と後からの追加にも有効）を用いる。
主判定の族は「その判定（シナリオ・p・窓）で候補になるシミュレーション済みの d 全て」：選んだ d と「最小サイズの確定」を
全ての要求値について同時に95%で保護する。v9.2 の表全体（最大200点）の同時保証は、より厳しい感度の列 `*_tablewide_*` に残す。固定Nの参考区間は別列。
実測点が未確定ならモデルで上書きしない。モデル支持（bootstrap>=95%）は別列で、データ保証ではない。
小さいサイズが未確定なら、保証された候補があっても最小費用確定とはしない。
Litinski列は文献誤り予算の中央値であり、両方式に同じ統計保証があるという比較ではない。
''')
            set_source(nb['cells'][60],(ROOT/'cells/decisions.py').read_text())
            for cell in nb['cells'][61:]:
                if cell['cell_type']=='markdown':set_source(cell,'## v10 の解釈\n出力CSVのデータ保証・モデル支持・未確定を区別する。データによる下限（`*_low_*`）とモデルによる外挿を混同しない。\n')
            embed='import types, sys\n_analysis_v10=types.ModuleType("analysis_v10")\nsys.modules["analysis_v10"]=_analysis_v10\nexec(compile('+repr(module)+',"analysis_v10.py","exec"),_analysis_v10.__dict__)\n'
            nb['cells'].insert(44,code(embed))
        else:
            if filename=='D4_noisy_simulation.ipynb':
                cfg=''.join(nb['cells'][43]['source'])
                cfg=cfg.replace('TIME_CAP, MAX_FAIL, WORKERS = 1200, 200, 4','WORKERS = 4').replace('TIME_CAP, MAX_FAIL, WORKERS = 60, 50, 2','WORKERS = 2').replace(', max_fail=100, time_cap=TIME_CAP // 2','').replace(', max_fail=100','').replace('EXTEND_SECONDS = 3600','')
                cfg += '\n# v9.2: fixed sample sizes; no failure-count or wall-clock stopping.\nSHOTS_PER_POINT = 400 if QUICK else 100000\nEXTEND_SHOTS = 100000\n'
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
                set_source(nb['cells'][47],run)
                calibration=''.join(nb['cells'][49]['source'])
                calibration=calibration.replace('def calibrate():\n', 'def calibrate():\n    if os.path.exists(CAL_CSV):\n        print("Reusing existing calibration CSV (choose a new output directory to recalibrate):", CAL_CSV)\n        return pd.read_csv(CAL_CSV)\n')
                set_source(nb['cells'][49],calibration)

            # No new physics: old physical validation remains applicable.
            nb['cells'].insert(1,markdown('物理回路・雑音・復号のコードはv9と同一。validationのINFOと未検証範囲を保持。\n'))
        (ROOT/filename).write_text(json.dumps(nb,ensure_ascii=False,indent=1))
    stats_embed='import types, sys\n_analysis_v10=types.ModuleType("analysis_v10")\nsys.modules["analysis_v10"]=_analysis_v10\nexec(compile('+repr(module)+',"analysis_v10.py","exec"),_analysis_v10.__dict__)\n'
    stats=dict(nbformat=4,nbformat_minor=0,metadata=dict(kernelspec=dict(display_name='Python 3',name='python3'),language_info=dict(name='python')),
        cells=[markdown('# v10 統計検証（CPU、単独Colabノート）\n\n固定Nの厳密な分布列挙、逐次停止時のconfidence sequence、カテゴリ再標本化を検査する。物理検証とは別。\n'),
               code(stats_embed),code((ROOT/'cells/statistics_validation.py').read_text())])
    (ROOT/'statistics_validation_v10.ipynb').write_text(json.dumps(stats,ensure_ascii=False,indent=1))

if __name__=='__main__':build()
