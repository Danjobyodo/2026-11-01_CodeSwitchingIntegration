import d4_v91_val_gen as V, pandas as pd
V.CFG.update(seed=20261102 + 4242, circuit_noise_preset="uniform", noise_model="circuit_level", dressing_treatment="exact", logical_colors="rgb")
rows = []
for p in [0.0015, 0.0025]:
    for L in [7, 9]:
        for kap in [0.0, 0.1, 0.25]:
            V.CFG["tf_decoder_kappa"] = {"depolarizing": 0.5, "phenomenological": 0.0, "circuit_level": kap}
            r = V.run_one_point_tf(L=L, p=p, shots=20000, noise_model="circuit_level")
            rows.append(dict(p=p, L=L, kappa_dec=kap, ler_charge=r["ler_charge"], lo=r["ler_charge_lower"], hi=r["ler_charge_upper"]))
            print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv("kappa_scan/d4_v9_1_decoder_kappa_check_circuit_level_uniform_L7-9.csv", index=False)
