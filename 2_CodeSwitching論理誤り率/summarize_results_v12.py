"""Recompute both study-2 metrics from the stored production CSVs (no new Monte Carlo).

Usage (in this folder): python summarize_results_v12.py [--output-dir <dir>]   -- about 10 seconds.
Writes (default: 本番結果/指標の再集計/):
  chsc_metrics_v12.csv   : every production point with both metrics recomputed from the class counts
  provenance.json        : SHA-256 of the source CSVs
  chsc_v12_crossings.csv : neighbouring-d crossings of P_L for the six production conditions (v12)
  chsc_v12_P_L.png       : P_L vs p of the six production conditions in one figure (v12; same drawing as the
                           summary figure of chsc_switch_v12.run_experiments)
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent/'本番結果'
CLASSES=['I','X','Y','Z','S','collapsed','flux_D4']

def summarize(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    files=sorted((ROOT/'chsc_v9_results').glob('chsc_v9_*.csv'))
    files=[p for p in files if not p.stem.endswith('_crossings')]
    files += [ROOT/'chsc_v3_results/chsc_v3_in_T_out_ideal.csv']
    rows=[];provenance=[]
    for file in files:
        df=pd.read_csv(file)
        if not {'case','shots',*[f'n_{c}' for c in CLASSES]}<=set(df):raise ValueError(f'invalid source: {file}')
        if not np.all(df[[f'n_{c}' for c in CLASSES]].sum(axis=1)==df.shots):raise ValueError('category totals differ')
        for _,r in df.iterrows():
            w={'I':0,'Z':1,'X':.5,'Y':.5,'S':.5,'collapsed':.5} if r['case']=='in_T_out' else {'I':0,'Z':1,'X':0,'Y':1,'S':.5,'collapsed':.5}
            n_eval=r.shots-r.n_flux_D4
            eps=sum(w[c]*r[f'n_{c}'] for c in w)/n_eval if n_eval else np.nan
            p_l=1-r.n_I/r.shots
            if not np.isclose(p_l,r.P_L) or not np.isclose(eps,r.mean_infidelity_excl_fluxD4):raise ValueError('stored metric differs')
            rows.append({**r.to_dict(),'P_L_recomputed':p_l,'infidelity_excl_fluxD4_recomputed':eps,
                         'evaluated_shots':n_eval,'analysis_version':'v12','source_file':str(file.relative_to(ROOT))})
        provenance.append(dict(file=str(file.relative_to(ROOT)),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),rows=len(df)))
    out=pd.DataFrame(rows)
    if out.duplicated(['case','switch_in_boundary','d','p']).any():raise ValueError('duplicate physical point')
    out.to_csv(output/'chsc_metrics_v12.csv',index=False)
    (output/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
    # v12: the summary figure and the crossings of all six conditions (replace the per-condition figures of v9)
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import chsc_switch_v12 as engine
    cr=[]
    for (case,b),df in out.groupby(['case','switch_in_boundary'],sort=False):
        for row in engine.estimate_crossings(df.sort_values(['d','p']),'P_L',seed=int(engine.CFG['seed'])):
            cr.append(dict(case=case,switch_in_boundary=b,**row))
    order={c:i for i,c in enumerate(engine.CASE_TITLES)}
    pd.DataFrame(cr).sort_values(['case','switch_in_boundary','d_a'],key=lambda s:s.map(order) if s.name=='case' else s).to_csv(output/'chsc_v12_crossings.csv',index=False)
    engine.plot_boundaries(out.sort_values('case',key=lambda s:s.map(order)),str(output/'chsc_v12_P_L.png'))
    print(f'Validated {len(out)} points, {int(out.shots.sum()):,} existing shots; no new Monte Carlo.')
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent/'本番結果'/'指標の再集計')
    summarize(p.parse_args().output_dir)
