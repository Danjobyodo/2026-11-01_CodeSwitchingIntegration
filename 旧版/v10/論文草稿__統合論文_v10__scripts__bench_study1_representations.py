"""Cost per shot of the twisted frame and the operator-level Pauli proxy (memory, phenomenological, p = 2%).

Used for Table 1 of the integrated paper. Generate the validation module first, then run in that folder:
    python 1_D4閾値/tools_v10/build_notebooks_v10.py --scripts <dir>
    cd <dir> && python <repo>/論文草稿/統合論文_v10/scripts/bench_study1_representations.py
Writes bench_study1_pheno_p0.02.json (copy in ../figures/). Times include decoding; one CPU core.
"""
import sys, time, json, os
src = open("d4_v10_val_script.py").read()
cut = src.index("\nvresults = {}")
import types
mod = types.ModuleType("benchmod"); sys.modules["benchmod"] = mod
exec(compile(src[:cut], "d4_v10_val_script.py", "exec"), mod.__dict__)
ns = mod.__dict__
g_ = ns
CFG, VCFG = g_["CFG"], g_["VCFG"]
CFG["out_dir"] = "out"; VCFG["out_dir"] = "out"
nm = "phenomenological"; p = 0.02
CFG["noise_model"] = nm
import numpy as np
rows = []
plan = {3: (4000, 400), 5: (2000, 200), 7: (1000, 100), 9: (500, 50)}
for L, (n_batch, n_shot) in plan.items():
    CFG["L_values"] = [L]
    t0 = time.time(); r = g_["run_one_point_tf"](L=L, p=p, shots=n_batch, noise_model=nm); tb = (time.time()-t0)/n_batch
    VCFG_L = VCFG["L"]; VCFG["L"] = L
    ctx = g_["build_validation_context"](nm, p, "rgb"); VCFG["L"] = VCFG_L
    g, stab = ctx["g"], ctx["stab"]
    res = {}
    for name in ("tf", "px"):
        b = g_["TFBackend"](g, stab, ctx["xt"], ctx["zt"]) if name == "tf" else g_["ProxyTorusBackend"](g, stab)
        if name == "px": b.xtab, b.ztab = ctx["xt"], ctx["zt"]
        rng = np.random.default_rng(11 + L)
        t0 = time.time()
        for s in range(n_shot):
            g_["protocol_shot"]([b], g, stab, ctx["nz"], ctx["jit"], ctx["closer"], ctx["order"], rng, xtab=ctx["xt"], ztab=ctx["zt"])
        res[name] = (time.time()-t0)/n_shot
    row = dict(L=L, n=9*L*L, tf_batched_ms=1e3*tb, tf_shot_loop_ms=1e3*res["tf"], proxy_shot_loop_ms=1e3*res["px"], ler_charge=r.get("ler_charge"))
    print(row, flush=True); rows.append(row)
json.dump(rows, open("bench_study1_pheno_p0.02.json", "w"), indent=1)
