import sys
import d4_v91_val_gen as V
V.CFG["seed"] = 20261102 + 999          # separate seed from the production runs (docstring of decoder_kappa_scan)
V.CFG["circuit_noise_preset"] = "uniform"
V.VCFG["out_dir"] = "kappa_scan"
import os; os.makedirs("kappa_scan", exist_ok=True)
for nm in sys.argv[1:]:
    V.CFG["noise_model"] = nm
    V.decoder_kappa_scan(nm)
