import sys, time, pandas as pd
import d4_v91_val_mod as M
rows = []
shots = {3: 2000, 5: 1000, 7: 400, 9: 200}
for nm, preset, p in [("depolarizing", "uniform", 0.10), ("phenomenological", "uniform", 0.03),
                      ("circuit_level", "uniform", 0.004), ("circuit_level", "legacy_v7", 0.004)]:
    M.CFG["circuit_noise_preset"] = preset
    M.CFG["noise_model"] = nm
    for L in [3, 5, 7, 9]:
        r = M.proxy_crosscheck(nm, L, p, shots[L], 20261102 + L, "rgb")
        r["circuit_noise_preset"] = preset if nm == "circuit_level" else "-"
        rows.append(r)
        print("PASSED", {k: r[k] for k in ["noise_model","circuit_noise_preset","L","shots","max_prob_deviation","max_fidelity_deviation","random_outcomes_tf","proxy_random","shots_compared_fidelity","seconds"]}, flush=True)
        pd.DataFrame(rows).to_csv("proxy_crosscheck_v9_1_full.csv", index=False)
