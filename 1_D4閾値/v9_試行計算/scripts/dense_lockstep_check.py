import sys, time
sys.path.insert(0, sys.argv[1])
import d4_v9_val_mod as _M; globals().update({k: v for k, v in vars(_M).items() if not k.startswith("__")})
print("JAX_AVAILABLE", JAX_AVAILABLE)
VCFG["L"] = 3
nm = sys.argv[2]; preset = sys.argv[3]; lc = sys.argv[4]; shots = int(sys.argv[5])
CFG["circuit_noise_preset"] = preset
CFG["noise_model"] = nm
lat = TriangulatedTorus.build(3); stab = build_d4_stabilizers(lat)
_, g_lc = _tf_geometry_cached(3, lc)
t0 = time.time()
dense = DenseBackend(g_lc, stab)
print("dense init %.1fs k=%d" % (time.time() - t0, g_lc.k), flush=True)
p = float(sys.argv[6]) if len(sys.argv) > 6 else float(VCFG["lockstep_p"][nm])
t0 = time.time()
res = lockstep_exactness_test(nm, p, shots, int(CFG["seed"]) + 5, dense, lc)
print("(B) PASSED", nm, preset, lc, res, "%.0fs" % (time.time() - t0))
