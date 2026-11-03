import sys
import numpy as np
import d4_v91_val_gen as M
M.CFG["circuit_noise_preset"] = "uniform"
# negative controls: each sabotage must make the cross-check fail
orig_measured = M.ErrorFrameTorus.measured
orig_lcz = M.ErrorFrameTorus.left_cz
def no_dressing(self, S, PA, PB, extraZ):           # forget the Pauli dressing of the CZ factors
    return orig_measured(self, S, PA[:0], PB[:0], extraZ)
def no_cz(self, pairs):                               # forget CZ parts of the error frame
    return None
def no_extraZ(self, S, PA, PB, extraZ):
    return orig_measured(self, S, PA, PB, None)
cases = [("no Pauli dressing", "phenomenological", "measured", no_dressing, 0.04),
         ("CZ in error frame dropped", "circuit_level", "left_cz", no_cz, 0.01),
         ("CZ(anc,data) fault Z dropped", "circuit_level", "measured", no_extraZ, 0.01)]
for name, nm, attr, fn, p in cases:
    setattr(M.ErrorFrameTorus, attr, fn)
    M.CFG["noise_model"] = nm
    try:
        r = M.proxy_crosscheck(nm, 3, p, 40, 777, "rgb")
        print("NEGATIVE CONTROL NOT DETECTED:", name, r)
    except AssertionError as e:
        print("detected (good):", name, "->", str(e)[:110])
    setattr(M.ErrorFrameTorus, "measured", orig_measured)
    setattr(M.ErrorFrameTorus, "left_cz", orig_lcz)
