# Data certificates use Beta-mixture confidence sequences (valid under the failure-count/time
# stopping and the later extensions of the MC). The PRIMARY family of one decision is the set of
# simulated candidate sizes d at that (scenario, p, window): the reported size and the
# "minimum resolved" statement are covered simultaneously for every target of that row.
# The table-wide family (all selected points, declared maximum 200) is kept as a stricter
# sensitivity column (`*_tablewide_*`); it is valid for claims about the whole table at once.
# The table-wide lower bound (`*_tablewide_d_low`, `*_tablewide_volume_low`) is written as well, so that
# statements about all rows together (e.g. 'at least x times in all ten conditions') can be checked with M=200.
from functools import lru_cache
CONFIDENCE = 0.95
TABLEWIDE_FAMILY_SIZE = 200  # declared maximum family including future points
if len(main)+len(quiet)>TABLEWIDE_FAMILY_SIZE:
    raise ValueError('Declare a larger confidence family before analyzing this many points')

def decision_family_size(s,p,w_):
    df = main if w_=='noisy' else quiet
    n = int(((df.scenario==s)&np.isclose(df.p,p,rtol=1e-10,atol=0)).sum())
    return max(1,n)

def point_data(s,d,p,w_):
    if d is None: return None
    df = main if w_=='noisy' else quiet
    rows_ = df[(df.scenario==s)&(df.d==d)&np.isclose(df.p,p,rtol=1e-10,atol=0)]
    if len(rows_)>1: raise ValueError('ambiguous point')
    return rows_.iloc[0] if len(rows_) else None

def eps_ci(row,cl=CONFIDENCE,family=None):
    w_ = row['window']
    fam = decision_family_size(row['scenario'],float(row['p']),w_) if family is None else family
    return stats.anytime_mean_cs(row,cl,fam)

def model_allowed(w_,d):
    return d>=W_DMIN if w_=='noisy' else True

@lru_cache(maxsize=None)
def _model_draws(s,d,p,w_,variant):
    return np.array([eps_K_model(s,d,p,w_,bt,variant) for bt in FITS[s]['boot']])

def kob_entry(s,p,target,w_,variant='main',family=None):
    fam = decision_family_size(s,p,w_) if family is None else family
    def dec(row): return stats.data_decision(row,target,CONFIDENCE,fam)['status']
    data_reached=[]; model_reached=[]
    for d in range(3,62,2):
        row=point_data(s,d,p,w_)
        if row is not None and dec(row)=='data_certified':
            data_reached.append(d)
        if model_allowed(w_,d):
            frac=np.mean(_model_draws(s,d,p,w_,variant)<=target)
            if frac>=0.95:model_reached.append(d)
    d=min(data_reached) if data_reached else None
    md=min(model_reached) if model_reached else None
    # Unsimulated smaller sizes cannot be rejected by a data certificate.
    smaller = [j for j in range(3,d,2)] if d is not None else []
    minimum_resolved = d is not None and all(point_data(s,j,p,w_) is not None and
          dec(point_data(s,j,p,w_))=='data_rejected' for j in smaller)
    possible=[j for j in range(3,62,2) if point_data(s,j,p,w_) is None or dec(point_data(s,j,p,w_))!='data_rejected']
    low=min(possible) if possible else None
    kc=kobayashi_cost(d) if d is not None else None
    return dict(status='data_certified' if d is not None else 'unresolved',d=d if d else '—',
        d_low=low if low else '—',basis=f'anytime_bounded_loss_family{fam}' if d else '—',family_size=fam,
        minimum_resolved=minimum_resolved,d_extrapolated=False,
        qubits=kc['qubits'] if kc else np.nan,time_steps=kc['time_steps'] if kc else np.nan,
        volume=kc['volume'] if kc else np.nan,volume_low=kobayashi_cost(low)['volume'] if low else np.nan,
        model_status='model_supported' if md else 'no_model_support',model_d=md if md else '—',
        model_volume=kobayashi_cost(md)['volume'] if md else np.nan,
        model_d_extrapolated=bool(md is not None and md>FITS[s]['d_max_data']))

point_rows=[]
for _,row in pd.concat([main,quiet]).iterrows():
    fam=decision_family_size(row['scenario'],float(row['p']),row['window'])
    lo,hi=eps_ci(row)
    tlo,thi=eps_ci(row,family=TABLEWIDE_FAMILY_SIZE)
    plo,phi=stats.bounded_mean_ci(row,CONFIDENCE,1)
    point_rows.append({**row.to_dict(),'lower_decision':lo,'upper_decision':hi,'decision_family_size':fam,
                       'lower_tablewide':tlo,'upper_tablewide':thi,'tablewide_family_size':TABLEWIDE_FAMILY_SIZE,
                       'lower_fixedN_reference':plo,'upper_fixedN_reference':phi})
DATA_INTERVALS=pd.DataFrame(point_rows)
DATA_INTERVALS.to_csv(f'{RESULTS}/data_intervals{OUT_SUFFIX}.csv',index=False)
rows=[]
for s in SCENARIOS:
    for p in P_EVAL:
        df=LIT[(s,p)]
        for target in TARGETS:
            ok=df[df.eps<=target]
            lit=ok.loc[ok.volume_steps.idxmin()] if len(ok) else None
            row=dict(scenario=s,p=p,target=target,p_extrapolated=bool(p<FITS[s]['p_min_bulk']),
                confidence=CONFIDENCE,tablewide_family_size=TABLEWIDE_FAMILY_SIZE,
                litinski_basis='central_literature_budget_not_confidence_certificate',
                litinski_protocol=lit.protocol if lit is not None else 'none in candidate set',
                litinski_eps=lit.eps if lit is not None else np.nan,
                litinski_qubits=lit.qubits if lit is not None else np.nan,
                litinski_time_steps=lit.time_steps if lit is not None else np.nan,
                litinski_volume=lit.volume_steps if lit is not None else np.nan)
            for prefix,window,var in [('kobayashi','noisy','main'),('kobayashi_diag','quiet','main'),
                                       ('kobayashi_W5','noisy','W5'),('kobayashi_altW','noisy','altW')]:
                row.update({f'{prefix}_{k}':v for k,v in kob_entry(s,p,target,window,var).items()})
                if var=='main':   # stricter sensitivity: table-wide family
                    tw=kob_entry(s,p,target,window,var,family=TABLEWIDE_FAMILY_SIZE)
                    row.update({f'{prefix}_tablewide_{k}':tw[k] for k in ('status','d','minimum_resolved','volume','d_low','volume_low')})  # incl. the lower bound
            rows.append(row)
CMP=pd.DataFrame(rows)
for prefix in ['kobayashi','kobayashi_diag','kobayashi_W5','kobayashi_altW']:
    CMP[f'ratio_{prefix}_over_litinski']=CMP[f'{prefix}_volume']/CMP.litinski_volume
    CMP[f'ratio_{prefix}_model_over_litinski']=CMP[f'{prefix}_model_volume']/CMP.litinski_volume
    CMP[f'ratio_{prefix}_low_over_litinski']=CMP[f'{prefix}_volume_low']/CMP.litinski_volume
CMP['ratio_kobayashi_tablewide_over_litinski']=CMP['kobayashi_tablewide_volume']/CMP.litinski_volume
# lower bound of the volume under the table-wide family (smallest size not rejected with M=200)
CMP['ratio_kobayashi_tablewide_low_over_litinski']=CMP['kobayashi_tablewide_volume_low']/CMP.litinski_volume
CMP['kobayashi_diag_volume_fsc8']=[kobayashi_cost_fsc8(d)['volume'] if d!='—' else np.nan for d in CMP.kobayashi_diag_d]
CMP['ratio_kobayashi_diag_fsc8_over_litinski']=CMP.kobayashi_diag_volume_fsc8/CMP.litinski_volume
for key,value in PROV.items():CMP[key]=value
print('Data certificates and model support are separate. Litinski uses a central budget model.')
CMP[['scenario','p','target','kobayashi_status','kobayashi_d','kobayashi_minimum_resolved','kobayashi_tablewide_status',
     'kobayashi_model_status','kobayashi_model_d','ratio_kobayashi_over_litinski','ratio_kobayashi_model_over_litinski']]
