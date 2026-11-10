"""Cost per shot of the twisted frame and the operator-level Pauli proxy (memory, phenomenological, p = 2%).

Used for Table 1 of the integrated paper.  Generate the validation module first, then run in that folder:
    python 1_D4閾値/tools_v11/build_notebooks_v11.py --scripts <dir>
    cd <dir> && python <repo>/論文草稿/統合論文_v11/scripts/bench_study1_representations.py
Writes bench_study1_pheno_p0.02.json (copy in ../figures/).  Times include decoding; one process.

v11: every measurement is preceded by a warm-up at the same size (JIT compilation, geometry and decoder
construction are not timed), is repeated REPEATS times, and the median, minimum and maximum are stored together
with the environment.  What is compared is these two implementations as they are: "tf_batched" is the production
engine (batched sampling), "tf_shot_loop" and "proxy_shot_loop" run through the same per-shot Python driver.
"""
import sys, time, json, os, platform, types
import numpy as np

REPEATS = 5
PLAN = {3: (2000, 200), 5: (1000, 100), 7: (500, 50), 9: (300, 30)}     # L: (shots batched, shots per-shot loop)
NOISE, P = "phenomenological", 0.02

src = open("d4_v11_val_script.py").read()
cut = src.index("\nvresults = {}")
mod = types.ModuleType("benchmod"); sys.modules["benchmod"] = mod
exec(compile(src[:cut], "d4_v11_val_script.py", "exec"), mod.__dict__)
g_ = mod.__dict__
CFG, VCFG = g_["CFG"], g_["VCFG"]
CFG["out_dir"] = "out"; VCFG["out_dir"] = "out"
CFG["noise_model"] = NOISE


def stats(xs):
    return dict(median_ms=1e3 * float(np.median(xs)), min_ms=1e3 * float(np.min(xs)), max_ms=1e3 * float(np.max(xs)))


def environment():
    import importlib.metadata as md
    cpu = ""
    try:
        cpu = next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name"))
    except Exception:
        pass
    vers = {}
    for name in ("numpy", "numba", "stim", "pymatching", "scipy"):
        try:
            vers[name] = md.version(name)
        except Exception:
            vers[name] = None
    return dict(cpu=cpu, logical_cpus=os.cpu_count(), python=platform.python_version(), versions=vers,
                threads={k: os.environ.get(k) for k in ("NUMBA_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
                code_version=g_.get("CODE_VERSION"), repeats=REPEATS, noise_model=NOISE, p=P)


rows = []
for L, (n_batch, n_shot) in PLAN.items():
    CFG["L_values"] = [L]
    g_["run_one_point_tf"](L=L, p=P, shots=50, noise_model=NOISE)                      # warm-up, not timed
    tb = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        g_["run_one_point_tf"](L=L, p=P, shots=n_batch, noise_model=NOISE)
        tb.append((time.perf_counter() - t0) / n_batch)
    VCFG_L = VCFG["L"]; VCFG["L"] = L
    ctx = g_["build_validation_context"](NOISE, P, "rgb"); VCFG["L"] = VCFG_L
    g, stab = ctx["g"], ctx["stab"]
    res = {}
    for name in ("tf", "px"):
        b = g_["TFBackend"](g, stab, ctx["xt"], ctx["zt"]) if name == "tf" else g_["ProxyTorusBackend"](g, stab)
        if name == "px":
            b.xtab, b.ztab = ctx["xt"], ctx["zt"]
        def run(n, seed):
            rng = np.random.default_rng(seed)
            for _ in range(n):
                g_["protocol_shot"]([b], g, stab, ctx["nz"], ctx["jit"], ctx["closer"], ctx["order"], rng,
                                    xtab=ctx["xt"], ztab=ctx["zt"])
        run(3, 1)                                                                         # warm-up, not timed
        ts = []
        for r in range(REPEATS):
            t0 = time.perf_counter(); run(n_shot, 11 + L + 100 * r); ts.append((time.perf_counter() - t0) / n_shot)
        res[name] = ts
    row = dict(L=L, n=9 * L * L, shots_batched=n_batch, shots_loop=n_shot, tf_batched=stats(tb),
               tf_shot_loop=stats(res["tf"]), proxy_shot_loop=stats(res["px"]))
    print(row, flush=True); rows.append(row)
json.dump(dict(environment=environment(), rows=rows), open("bench_study1_pheno_p0.02.json", "w"), indent=1)
