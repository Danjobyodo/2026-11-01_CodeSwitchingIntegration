import d4_v91_main_gen as M, pandas as pd, numpy as np
M.CFG.update(noise_model="circuit_level", circuit_noise_preset="uniform")
print("kappa_dec used:", M.decoder_kappa("circuit_level"))
M.CFG["circuit_noise_preset"]="legacy_v7"; print("legacy kappa_dec:", M.decoder_kappa("circuit_level")); M.CFG["circuit_noise_preset"]="uniform"
rows=[]
for p in [1.0e-3, 1.3e-3, 1.7e-3, 2.2e-3, 3.0e-3]:
    for L in [3,5,7]:
        r=M.run_one_point_tf(L=L,p=p,shots=4000,noise_model="circuit_level"); rows.append(r)
        print(f"L={L} p={p:.1e} charge={r['ler_charge']:.4f} [{r['ler_charge_lower']:.4f},{r['ler_charge_upper']:.4f}] kappa={r['tf_decoder_kappa']}", flush=True)
df=pd.DataFrame(rows); df.to_csv("pilot_cl_uniform_kappa0.1.csv",index=False)
def cross(df):
    out=[]; Ls=sorted(df.L.unique())
    for a,b in zip(Ls,Ls[1:]):
        A=df[df.L==a].sort_values('p'); B=df[df.L==b].sort_values('p'); x=np.log(A.p.values); d=np.log(B.ler_charge.values)-np.log(A.ler_charge.values)
        for i in range(len(x)-1):
            if d[i]*d[i+1]<0: t=d[i]/(d[i]-d[i+1]); out.append((a,b,float(np.exp(x[i]+t*(x[i+1]-x[i])))))
    return out
print(cross(df))
