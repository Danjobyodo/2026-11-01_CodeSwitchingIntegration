# Changelog

Revision history of the code of studies 1–3. The current version of every study is v13. Version numbers were
unified across the studies at v9. "Physics" below means the simulated circuits, noise, decoders, random-number use
and decision rules; versions that do not change the physics reproduce the stored results exactly.

## v13 (2026-11-13 – 2026-11-14)

* All studies: version label v13; output names `d4_v13_*`, `chsc_v13_*`, `results_v13/`, `figures_v13/`.
  Results written by v10–v12 (study 1 checkpoints, study 2 CSVs) are continued when the configuration is the same.
* Publication cleanup. Internal notes were removed from comments and notebook text: references to review rounds,
  to files outside the repository and to internal drafts, and per-line version tags. The revision history is
  kept here instead. Every comment-only edit was checked to leave the abstract syntax tree of the code unchanged.
* Study 1: the self-check of the previous-study surrogate (`engine="stim_surrogate"`) failed with the default
  `p_min=None`. It now uses the resolved p range. The production engine `twisted_frame` was not affected.
  The unused field `TFGeometry.dummy` and the unused `tsim` import were removed.
* Study 2: the logical class "S" of the final state is defined in the code (|±i⟩: the target rotated by a
  logical S or S†).
* Study 3: the unused parameter `dem_noise` of `ChargeDecoder` and unused local variables were removed. The
  decoder model always used the noise of the simulation, so nothing changes. The figures are drawn from the
  result CSVs (`figures_v13.py`), with 95 % decision intervals and points without failures shown. The
  docstring of `single_fault_scan` explains the sampling of the switch-out CZ faults. The notebooks state that
  the argument `L` of the code is the code distance d of the paper.
* Physics unchanged. Verified: identical outputs before and after the cleanup (study 1 small runs for all
  noise models; study 3 QUICK simulation and the comparison notebook). The only exception is the
  `analysis_sha256` column, which changes with any edit of the analysis module.

## v12 (2026-11-12)

* Outputs reduced to what the studies need:
  * Study 1: one figure with three panels per run; no PDF by default.
  * Study 2: one crossings table and one figure for all conditions.
* Run times are given at the top of every notebook.
* Study 3: the physical validation with `QUICK=True` no longer requires all 16 outcome patterns of the V7 check
  (40 branches are too few); the chi-squared test is kept.

## v11 (2026-11-10)

* Study 2: resume also finds result CSVs written under the file names of earlier equivalent versions.
* Study 3:
  * The table-wide lower bound of the volume was added.
  * Additional MC chunks are appended in the columns of the existing production CSV.

## v10 (2026-11-03 – 2026-11-05)

* Study 3: data certificates use Beta-mixture confidence sequences. The decision family is the set of simulated
  sizes of one decision; the table-wide family is kept as a stricter sensitivity.
* Labels only in studies 1–2.

## v9.1 / v9.2 (2026-11-02)

* Study 1:
  * v9.1: independent Pauli-proxy engine (validation (E)) cross-checked against the twisted frame for L = 3–9.
  * v9.1: decoder prior κ_dec = 0.1 for the circuit-level definition `uniform`.
  * v9.2: resume from atomic JSON checkpoints (only for the identical configuration); long runs are not executed
    by default.
* Study 3, v9.2:
  * Multinomial (0, ½, 1) description model of the output error.
  * Fixed sample sizes (no stopping on failure counts or wall-clock time).

## v9 (2026-11-02)

* Study 1:
  * Circuit-level noise definition `uniform` (the same as study 3), with the earlier definition kept as `legacy_v7`.
  * No future boundary of the JIT decoder without measurement errors.
  * Diagnostics of residual fluxes; production driver `run_production()` with control experiments.
* Study 2:
  * The `noisy` boundary continues the decoding across U (joint flux / charge decoding, as in study 3).
  * Optional Z-only rounds before U (`n_pre_u`).
* Study 3: physics libraries (circuits, noise, decoders) used for the production Monte Carlo (5.54 M shots).

## Earlier versions

* Study 1:
  * v6: twisted-frame engine; corrected cup-product order of the green checks.
  * v7: separate charge / flux / combined metrics, control experiments (`dressing_treatment`), circuit-level
    decoder prior calibrated from the fault tables, and the stored production data (10⁴ shots per point).
* Study 2:
  * v1: geometry, protocol, decoders and a Z4 twisted-frame engine, now the independent reference of the
    validation.
  * v2: the Pauli-proxy engine on Stim.
  * v3: run management; production of the `ideal` boundary.
* Study 3, v4–v8: construction and validation of the noiseless protocol, of the distillation layouts and of the
  noisy simulation.
