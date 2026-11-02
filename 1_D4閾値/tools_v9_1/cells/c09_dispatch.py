def calc_agresti_coull_interval(
    n_trials: int,
    n_failures: int,
    alpha: float = 0.05,
) -> Tuple[float, float, float]:
    if n_trials == 0:
        return 0.0, 0.0, 0.0

    z = norm.ppf(1 - alpha / 2) if SCIPY_AVAILABLE else 1.96
    n_tilde = n_trials + z ** 2
    p_tilde = (n_failures + z ** 2 / 2) / n_tilde
    se_tilde = math.sqrt(p_tilde * (1 - p_tilde) / n_tilde)
    return (
        p_tilde,
        max(0.0, p_tilde - z * se_tilde),
        min(1.0, p_tilde + z * se_tilde),
    )


def _reshape_bool_matrix(arr: np.ndarray, shots: int, width: int) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.bool_)
    if width == 0:
        return np.zeros((shots, 0), dtype=np.bool_)
    if arr.ndim == 1:
        if shots == 1 and arr.size == width:
            return arr.reshape(1, width)
        if width == 1 and arr.size == shots:
            return arr.reshape(shots, 1)
    return arr.reshape(shots, width)


def _sample_dem(dem: "stim.DetectorErrorModel", shots: int) -> Tuple[np.ndarray, np.ndarray]:
    sampler = dem.compile_sampler()
    try:
        dets, obs = sampler.sample(shots, separate_observables=True)
    except TypeError:
        out = sampler.sample(shots)
        if isinstance(out, tuple) and len(out) >= 2:
            dets, obs = out[0], out[1]
        else:
            arr = np.asarray(out, dtype=np.bool_)
            nd = dem.num_detectors
            dets, obs = arr[:, :nd], arr[:, nd:]

    dets = _reshape_bool_matrix(np.asarray(dets, dtype=np.bool_), shots, dem.num_detectors)
    obs = _reshape_bool_matrix(np.asarray(obs, dtype=np.bool_), shots, dem.num_observables)
    return dets, obs


def _decode_observables(
    matcher: "pymatching.Matching",
    dets: np.ndarray,
    n_observables: int,
) -> np.ndarray:
    pred = matcher.decode_batch(dets)
    pred = np.asarray(pred, dtype=np.bool_)
    return _reshape_bool_matrix(pred, dets.shape[0], n_observables)


def _estimate_failure_rate(
    arts: DemXArtifacts,
    *,
    shots: int,
) -> float:
    matcher = pymatching.Matching.from_detector_error_model(arts.dem)
    dets, obs = _sample_dem(arts.dem, shots)
    pred = _decode_observables(matcher, dets, arts.n_observables)
    return float(np.mean(np.any(pred != obs, axis=1)))


def _resolve_noise_model_name(name: str) -> str:
    aliases = {
        "depolarizing": "depolarizing_surrogate_v2",
        "depolarizing_surrogate_v2": "depolarizing_surrogate_v2",
        "depolarizing_graphlike_dressed": "depolarizing_surrogate_v2",
        "depolarizing_effective_xcheck": "depolarizing_surrogate_v2",
        "phenomenological": "phenomenological",
        "circuit_level": "circuit_level",
    }
    if name not in aliases:
        raise ValueError(f"Unknown noise_model: {name}")
    return aliases[name]


def _resolve_rounds(model_name: str, L: int) -> int:
    """v6: depolarizing（符号容量型）は depolarizing_rounds を優先。それ以外は旧版通り rounds=None -> L。"""
    if model_name == "depolarizing_surrogate_v2" and CFG.get("depolarizing_rounds") is not None:
        return int(CFG["depolarizing_rounds"])
    return L if CFG["rounds"] is None else int(CFG["rounds"])


def run_one_point(
    *,
    L: int,
    p: float,
    shots: int,
    noise_model: str,
    depolarizing_overrides: Optional[Dict[str, object]] = None,
    phenomenological_overrides: Optional[Dict[str, object]] = None,
) -> Dict[str, float]:
    if stim is None or pymatching is None:
        raise RuntimeError("Stim and PyMatching are required.")

    if str(CFG.get("engine", "stim_surrogate")) == "twisted_frame":  # v6 既定エンジン
        if depolarizing_overrides or phenomenological_overrides:
            raise ValueError("overrides are only supported by engine='stim_surrogate'")
        return run_one_point_tf(L=L, p=p, shots=shots, noise_model=noise_model)

    model_name = _resolve_noise_model_name(str(noise_model))
    lat = TriangulatedTorus.build(L)
    stabs = build_d4_stabilizers(lat)
    rounds = _resolve_rounds(model_name, L)

    if model_name == "phenomenological":
        pheno = phenomenological_overrides or {}
        arts = build_phenomenological_x_circuit(
            stab=stabs,
            rounds=rounds,
            p=p,
            data_scale=pheno.get("data_scale"),
            meas_scale=pheno.get("meas_scale"),
            kickback_scale=pheno.get("kickback_scale"),
        )
    elif model_name == "depolarizing_surrogate_v2":
        overrides = depolarizing_overrides or {}
        arts = build_depolarizing_x_circuit(
            stab=stabs,
            rounds=rounds,
            p=p,
            data_scale=overrides.get("data_scale"),
            meas_scale=overrides.get("meas_scale"),
            dressing_scale=overrides.get("dressing_scale"),
            dressing_mode=overrides.get("dressing_mode"),
        )
    elif model_name == "circuit_level":
        arts = build_circuit_level_x_circuit(stab=stabs, rounds=rounds, p=p)
    else:
        raise AssertionError("unreachable")

    matcher = pymatching.Matching.from_detector_error_model(arts.dem)
    # v7: 元の回路から seed 付きで標本化（DEM は復号器の重みにだけ使う）
    seed = int(np.random.SeedSequence([int(CFG.get("seed", 0)), int(L), int(round(p * 1e12)), 7]).generate_state(1)[0])
    dets, obs = arts.circuit.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    pred = _decode_observables(matcher, dets, arts.n_observables)
    failures = np.any(pred != obs, axis=1)
    n_failures = int(np.sum(failures))

    alpha = 1.0 - float(CFG["confidence_level"])
    ac_p, ac_lower, ac_upper = calc_agresti_coull_interval(shots, n_failures, alpha)
    ler = n_failures / shots

    return {
        "engine": "stim_surrogate",
        "noise_model": str(noise_model),
        "L": float(L),
        "rounds": float(rounds),
        "p": float(p),
        "shots": float(shots),
        "n_failures": float(n_failures),
        "n_trials": float(shots),
        "logical_error_rate": float(ler),
        "ler_lower": float(ac_lower),
        "ler_upper": float(ac_upper),
        "ler_agresti_coull_center": float(ac_p),
        "n_detectors": float(arts.dem.num_detectors),
        "n_observables": float(arts.n_observables),
    }


def run_self_checks() -> Dict[str, object]:
    if stim is None or pymatching is None:
        raise RuntimeError("Stim and PyMatching are required for self-checks.")

    shots = int(CFG["self_check_shots"])
    L = int(CFG["L_values"][0])
    test_p = float(math.sqrt(float(CFG["p_min"]) * float(CFG["p_max"])))
    lat = TriangulatedTorus.build(L)
    stabs = build_d4_stabilizers(lat)
    rounds = _resolve_rounds("depolarizing_surrogate_v2", L)

    zero = run_one_point(
        L=L,
        p=0.0,
        shots=shots,
        noise_model="depolarizing_surrogate_v2",
    )
    if zero["n_failures"] != 0.0:
        raise AssertionError("p=0 should give LER=0 for the surrogate model.")

    arts = build_depolarizing_x_circuit(stab=stabs, rounds=rounds, p=test_p)
    matcher = pymatching.Matching.from_detector_error_model(arts.dem)
    dets, obs = _sample_dem(arts.dem, shots)
    pred = _decode_observables(matcher, dets, arts.n_observables)
    if pred.shape != obs.shape:
        raise AssertionError("Shape mismatch should be impossible in ver.2.")

    baseline = build_depolarizing_approx_baseline_circuit(
        stab=stabs,
        rounds=rounds,
        p=test_p,
    )
    off = build_depolarizing_x_circuit(
        stab=stabs,
        rounds=rounds,
        p=test_p,
        dressing_mode="off",
        dressing_scale=0.0,
    )
    if off.n_observables != baseline.n_observables:
        raise AssertionError("Off mode must preserve observable count.")
    if off.dem.num_detectors != baseline.dem.num_detectors:
        raise AssertionError("Off mode should preserve detector count.")
    baseline_ler = _estimate_failure_rate(baseline, shots=shots)
    off_ler = _estimate_failure_rate(off, shots=shots)
    if abs(off_ler - baseline_ler) > 0.20:
        raise AssertionError("Off mode drifted too far from the baseline proxy.")

    scales = [0.0, 0.15, 0.30]
    rate_profile = []
    for scale in scales:
        probe = build_depolarizing_x_circuit(
            stab=stabs,
            rounds=rounds,
            p=test_p,
            dressing_mode="pairwise_graphlike",
            dressing_scale=scale,
        )
        dets_s, obs_s = _sample_dem(probe.dem, shots)
        pred_s = _decode_observables(
            pymatching.Matching.from_detector_error_model(probe.dem),
            dets_s,
            probe.n_observables,
        )
        rate_profile.append(float(np.mean(np.any(pred_s != obs_s, axis=1))))

    if not (rate_profile[0] <= rate_profile[1] + 0.15 and rate_profile[1] <= rate_profile[2] + 0.15):
        raise AssertionError("Dressing sweep should vary continuously as the scale increases.")

    small_sweep = run_one_point(
        L=L,
        p=test_p,
        shots=shots,
        noise_model="depolarizing_surrogate_v2",
    )

    return {
        "p_zero_ler": zero["logical_error_rate"],
        "shape": {"pred": tuple(pred.shape), "obs": tuple(obs.shape)},
        "detectors": arts.dem.num_detectors,
        "observables": arts.n_observables,
        "baseline_detectors": baseline.dem.num_detectors,
        "off_detectors": off.dem.num_detectors,
        "baseline_ler": baseline_ler,
        "off_ler": off_ler,
        "dressing_rate_profile": dict(zip(scales, rate_profile)),
        "small_sweep_ler": small_sweep["logical_error_rate"],
    }


def run_experiments() -> pd.DataFrame:
    if stim is None or pymatching is None:
        raise RuntimeError("Stim and PyMatching are required.")

    L_values = [int(L) for L in CFG["L_values"]]
    shots = int(CFG["shots"])
    noise_model = _resolve_noise_model_name(str(CFG["noise_model"]))
    engine = str(CFG.get("engine", "stim_surrogate"))
    # v6: p_min/p_max/out_* が None なら、ノイズモデルごとの推奨値・自動ファイル名を使う
    rec_key = str(CFG["noise_model"])
    if rec_key == "circuit_level" and engine == "twisted_frame" and str(CFG.get("circuit_noise_preset")) == "uniform":
        rec_key = "circuit_level/uniform"     # v9: 回路雑音の定義ごとの推奨範囲
    rec = RECOMMENDED_P_RANGE.get(rec_key, (CFG["p_min"], CFG["p_max"]))
    p_min = float(rec[0] if CFG["p_min"] is None else CFG["p_min"])
    p_max = float(rec[1] if CFG["p_max"] is None else CFG["p_max"])
    p_n = int(CFG["p_n"])
    treat = str(CFG.get("dressing_treatment", "exact"))
    tag = f"d4_v9_1_X_memory_{CFG['noise_model']}_{engine}" + ("" if (engine != "twisted_frame" or treat == "exact") else f"_{treat}")
    if noise_model == "circuit_level" and engine == "twisted_frame":
        tag += f"_{CFG.get('circuit_noise_preset', 'legacy_v7')}"   # v9: 回路雑音の定義をファイル名に
    out_dir = str(CFG.get("out_dir") or ".")
    os.makedirs(out_dir, exist_ok=True)
    out_csv = str(CFG["out_csv"] or os.path.join(out_dir, tag + ".csv"))
    out_png = str(CFG["out_png"] or os.path.join(out_dir, tag + ".png"))
    p_values = [p_min] if p_n == 1 else list(np.exp(np.linspace(np.log(p_min), np.log(p_max), p_n)))

    if CFG.get("print_geometry_summary", True):
        lat0 = TriangulatedTorus.build(L_values[0])
        st0 = build_d4_stabilizers(lat0)
        summary = summarize_geometry(st0)
        print("[D4 X-Stabilizer Geometry Summary]")
        print(
            f"  L={L_values[0]} vertices={int(summary['vertices'])} "
            f"edges={int(summary['edges'])} triangles={int(summary['triangles'])}"
        )
        print(
            f"  X checks={int(summary['x_checks'])} unique dressing pairs={int(summary['unique_dressing_pairs'])}"
        )
        print(
            f"  SrX CZ-pairs per vertex(avg)={summary['avg_red_pairs_per_vertex']:.2f} "
            f"max dressing incidence={int(summary['max_dressing_incidence'])}"
        )
        if engine != "twisted_frame" and noise_model == "depolarizing_surrogate_v2":
            # v9: 旧研究のサロゲートの説明は、そのサロゲートを使うとき（engine="stim_surrogate"）だけ表示する（R1-8）
            print("  surrogate=effective graphlike depolarizing (not exact circuit-level depolarizing)")
            print(
                "  mode="
                f"{CFG['depolarizing_dressing_mode']} "
                f"dressing_scale={CFG['depolarizing_dressing_scale']:.3f} "
                f"data_scale={CFG['depolarizing_data_scale']:.3f} "
                f"meas_scale={CFG['depolarizing_meas_scale']:.3f}"
            )
        elif engine != "twisted_frame" and noise_model == "phenomenological":
            print("  surrogate=phenomenological with per-CZ-pair Z kickback")
            print(
                f"  kickback_scale={CFG['phenomenological_kickback_scale']:.3f} "
                f"data_scale={CFG['phenomenological_data_scale']:.3f} "
                f"meas_scale={CFG['phenomenological_meas_scale']:.3f}"
            )
        if engine == "twisted_frame":
            print("  [v9] engine=twisted_frame: dressed X checks are measured EXACTLY (non-commutativity included);")
            print(f"       dressing_treatment={treat}  (exact = D4 code; none / kappa_injection = control experiments)")
            if treat == "kappa_injection":
                print("       control experiment: bare checks + previous-study Z injection r=kappa*c*p "
                      f"(kappa: depol {CFG['depolarizing_dressing_scale']}, pheno {CFG['phenomenological_kickback_scale']}, "
                      f"circuit {CFG['circuit_kickback_scale']})")
            if noise_model == "circuit_level":
                print(f"       circuit_noise_preset={CFG.get('circuit_noise_preset')} "
                      "(uniform = study 3 scenario B / Takada App. A2; legacy_v7 = v7 production)")
            print(f"       jit_future_boundary={CFG.get('jit_future_boundary', 'always')}")
            print(f"       primary failure metric = {CFG['failure_metric']} (charge = X-stabilizer side, conditioned on flux success)")
            print(f"       charge-decoder prior: tf_decoder_kappa={decoder_kappa(str(CFG['noise_model']))}, "
                  f"cl_decoder_prior={CFG.get('cl_decoder_prior', 'calibrated')}")
            print(f"       logical_colors={CFG['logical_colors']} x_check_order={CFG['x_check_order']} "
                  f"jit_boundary_offset={CFG['jit_boundary_offset']} rounds={_resolve_rounds(noise_model, L_values[0])} (L={L_values[0]})")
        else:
            print("  [v9] engine=stim_surrogate: PREVIOUS-STUDY surrogate (bare MPP + r=kappa*c*p); non-commutativity NOT modeled.")
        print()

    if bool(CFG.get("save_manifest", True)):
        save_manifest(os.path.splitext(out_csv)[0] + "_manifest.json", extra=dict(p_values=[float(x) for x in p_values]))

    if bool(CFG.get("run_self_checks", False)) and engine == "twisted_frame":
        print("[Self-checks v9]")
        for key, val in run_self_checks_v6().items():
            print(f"  {key}: {val}")
        print()
    elif bool(CFG.get("run_self_checks", False)):
        print("[Self-checks]")
        checks = run_self_checks()
        print(f"  p=0 LER={checks['p_zero_ler']:.6f}")
        print(f"  pred/obs shape={checks['shape']['pred']} / {checks['shape']['obs']}")
        print(f"  off/baseline LER={checks['off_ler']:.6f} / {checks['baseline_ler']:.6f}")
        print(f"  dressing profile={checks['dressing_rate_profile']}")
        print(f"  small-shot LER={checks['small_sweep_ler']:.6f}")
        print()

    rows: List[Dict[str, float]] = []
    print(
        "Starting sweep "
        f"(noise={noise_model}, shots={shots}, CI={CFG['confidence_level'] * 100:.0f}% AC)..."
    )
    start = time.time()

    for L in L_values:
        for p in p_values:
            res = run_one_point(L=L, p=float(p), shots=shots, noise_model=noise_model)
            rows.append(res)
            pd.DataFrame(rows).to_csv(out_csv, index=False)  # 1 点ごとにチェックポイント保存
            extra = ""
            if engine == "twisted_frame":
                extra = (f" | charge={res['ler_charge']:.5f} flux={res['ler_flux']:.5f} "
                         f"combined={res['ler_combined']:.5f}")
            print(
                f"  [ok] L={L:2d} | p={p:.4e} | "
                f"LER={res['logical_error_rate']:.5f} "
                f"(95% CI: [{res['ler_lower']:.5f}, {res['ler_upper']:.5f}])" + extra
            )

    print(f"Sweep completed in {time.time() - start:.2f} seconds.\n")

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"Saved CSV: {out_csv}")

    fig, ax = plt.subplots(figsize=(8, 6))
    palette = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:brown"]
    for idx, L in enumerate(L_values):
        sub = df[df["L"] == float(L)].sort_values("p")
        x = sub["p"].to_numpy()
        y = np.maximum(sub["logical_error_rate"].to_numpy(), 1e-10)
        y_lower = sub["ler_lower"].to_numpy()
        y_upper = sub["ler_upper"].to_numpy()
        yerr_low = np.maximum(0.0, y - y_lower)
        yerr_high = np.maximum(0.0, y_upper - y)
        ax.errorbar(
            x,
            y,
            yerr=[yerr_low, yerr_high],
            fmt="-o",
            capsize=4,
            label=f"L={L}",
            color=palette[idx % len(palette)],
            alpha=0.85,
        )

    display_names = {
        # v6: 測定誤りなし（符号容量型）のときはそれが分かるように表示
        "depolarizing": "Depolarizing (code capacity)" if float(CFG["depolarizing_meas_scale"]) == 0.0 else "Depolarizing",
        "phenomenological": "Phenomenological",
        "circuit_level": "Circuit-level",
    }
    model_display = display_names.get(str(CFG["noise_model"]), str(CFG["noise_model"]))

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"Physical error rate $p$", fontsize=20)
    ylab = {"charge": r"$P_L$ (X-stabilizer / charge)", "combined": r"$P_L$ (charge or flux)",
            "flux": r"$P_L$ (flux)"}.get(str(CFG.get("failure_metric", "charge")), r"Logical error rate $P_L$")
    ax.set_ylabel(ylab if engine == "twisted_frame" else r"Logical error rate $P_L$", fontsize=20)
    ax.set_title(model_display, fontsize=30, fontweight="bold", pad=14)
    ax.tick_params(axis="both", which="major", labelsize=16)
    ax.grid(True, which="major", linestyle="-", alpha=0.7)
    ax.grid(True, which="minor", linestyle=":", alpha=0.3)
    ax.legend(fontsize=18)
    ax.text(
        0.98, 0.02, f"{shots} shots, 95% AC CI, engine={engine}" + (f", {treat}" if engine == "twisted_frame" and treat != "exact" else ""),
        transform=ax.transAxes, ha="right", va="bottom",
        fontsize=11, alpha=0.6,
    )
    fig.tight_layout()

    fig.savefig(out_png, dpi=200)
    print(f"Saved PNG: {out_png}")
    if bool(CFG.get("save_pdf", False)):
        pdf_path = os.path.splitext(out_png)[0] + ".pdf"
        fig.savefig(pdf_path)
        print(f"Saved PDF: {pdf_path}")

    if engine == "twisted_frame":
        plot_components(df, L_values, os.path.splitext(out_png)[0] + "_components.png", model_display)

    # 隣り合う L の曲線の交点（記述的な推定。有限サイズスケーリングではない）。v7: 指標ごとに出す
    try:
        metrics = list(METRIC_KEYS) if engine == "twisted_frame" else [None]
        allrows = []
        print("\n[Pairwise crossings of neighbouring L (descriptive; log-log interpolation, binomial bootstrap)]")
        for met in metrics:
            cross = estimate_crossings(df, metric=met)
            for row in cross:
                row["metric"] = met or "logical_error_rate"
                allrows.append(row)
                print("  [{}] L={}-{}: crossings={} ; bootstrap 68% / 95% interval (unique-crossing draws) = {} / {} ; "
                      "draws without/with multiple crossings: {} / {}".format(
                          row["metric"], row["L_a"], row["L_b"], ["%.4e" % c for c in row["crossings"]],
                          row["ci68"], row["ci95"], row["no_crossing_draws"], row["multiple_crossing_draws"]))
        pd.DataFrame(allrows).to_csv(os.path.splitext(out_csv)[0] + "_crossings.csv", index=False)
    except Exception as exc:  # noqa: BLE001
        print(f"[crossing estimate skipped: {exc}]")

    return df




def estimate_crossings(df: pd.DataFrame, n_boot: int = 400, metric: Optional[str] = None) -> List[Dict[str, object]]:
    """隣り合う L の LER 曲線の交点を log-log 線形補間で求め、二項分布（Jeffreys 事後）で揺らして区間を付ける。
    記述的な推定であり、有限サイズスケーリングによる閾値推定ではない。
    metric: None なら主指標（logical_error_rate / n_failures / n_trials）、"charge"/"combined"/"flux" ならその指標。"""
    col_r, col_k, col_n = ("logical_error_rate", "n_failures", "n_trials") if metric is None else \
        (f"ler_{metric}", f"n_fail_{metric}", f"n_trials_{metric}")
    if col_n not in df.columns:
        col_n = "shots"
    rng = np.random.default_rng(int(CFG.get("seed", 0)) + 917)
    rows = []
    sizes = sorted(df["L"].unique())
    for a, b in zip(sizes[:-1], sizes[1:]):
        u = df[df["L"] == a].sort_values("p")
        v = df[df["L"] == b].sort_values("p")
        if not np.allclose(u["p"].to_numpy(), v["p"].to_numpy()):
            raise ValueError("p grids differ between L values")
        p = u["p"].to_numpy()

        def roots(ya, yb):
            y = np.log(np.maximum(ya, 1e-12)) - np.log(np.maximum(yb, 1e-12))
            out = []
            for i in range(len(p) - 1):
                if y[i] * y[i + 1] < 0:
                    lp = np.log(p[i]) - y[i] * (np.log(p[i + 1]) - np.log(p[i])) / (y[i + 1] - y[i])
                    out.append(float(np.exp(lp)))
            return out

        est = roots(u[col_r].to_numpy(), v[col_r].to_numpy())
        draws, none_, multi = [], 0, 0
        for _ in range(n_boot):
            ka, na = u[col_k].to_numpy(), u[col_n].to_numpy()
            kb, nb = v[col_k].to_numpy(), v[col_n].to_numpy()
            r = roots(rng.beta(ka + 0.5, na - ka + 0.5), rng.beta(kb + 0.5, nb - kb + 0.5))
            if len(r) == 1:
                draws.append(r[0])
            elif not r:
                none_ += 1
            else:
                multi += 1
        ci68 = ["%.4e" % q for q in np.quantile(draws, [0.16, 0.84])] if draws else None
        ci95 = ["%.4e" % q for q in np.quantile(draws, [0.025, 0.975])] if draws else None
        rows.append(dict(L_a=int(a), L_b=int(b), crossings=est, ci68=ci68, ci95=ci95,
                         unique_draws=len(draws), no_crossing_draws=none_, multiple_crossing_draws=multi))
    return rows


def run_self_checks_v6() -> Dict[str, object]:
    """v6 (twisted_frame) の自己診断。"""
    L = int(CFG["L_values"][0])
    stab = build_d4_stabilizers(TriangulatedTorus.build(L))
    op_nc, flat_nc = count_noncommuting_x_check_pairs(stab)
    if flat_nc != 0:
        raise AssertionError("dressed X checks must commute on the flat subspace (geometry bug)")
    shots = int(CFG["self_check_shots"])
    samp = sample_tf_memory(str(CFG["noise_model"]), L, 0.0, shots, int(CFG.get("seed", 0)))
    if samp["dets"].any():
        raise AssertionError("p=0 must give no detection events")
    zero = run_one_point_tf(L=L, p=0.0, shots=shots, noise_model=str(CFG["noise_model"]))
    if zero["n_fail_combined"] != 0:
        raise AssertionError("p=0 must give no logical failures")
    return {"L": L, "operator-level noncommuting X-check pairs": op_nc,
            "noncommuting pairs on the flat subspace (must be 0)": flat_nc,
            "p=0 detection events": int(samp["dets"].sum()), "p=0 failures": int(zero["n_fail_combined"])}


def plot_components(df: pd.DataFrame, L_values, out_png: str, title: str) -> None:
    """v7: 3 つの指標（charge / flux / combined）を並べた図。"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), sharex=True)
    palette = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:brown"]
    names = {"charge": "charge (X-stabilizer), flux-success shots", "flux": "flux (Z-stabilizer)",
             "combined": "combined (charge or flux)"}
    for ax, met in zip(axes, ("charge", "flux", "combined")):
        for idx, L in enumerate(L_values):
            sub = df[df["L"] == float(L)].sort_values("p")
            y = np.maximum(sub[f"ler_{met}"].to_numpy(), 1e-10)
            ax.errorbar(sub["p"], y, yerr=[np.maximum(0, y - sub[f"ler_{met}_lower"]), np.maximum(0, sub[f"ler_{met}_upper"] - y)],
                        fmt="-o", capsize=3, label=f"L={L}", color=palette[idx % len(palette)], alpha=0.85)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(names[met], fontsize=13)
        ax.set_xlabel(r"$p$", fontsize=14)
        ax.grid(True, which="major", alpha=0.7)
        ax.grid(True, which="minor", linestyle=":", alpha=0.3)
    axes[0].set_ylabel(r"$P_L$", fontsize=14)
    axes[0].legend(fontsize=11)
    fig.suptitle(title, fontsize=16, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    if bool(CFG.get("save_pdf", False)):
        fig.savefig(os.path.splitext(out_png)[0] + ".pdf")
    print(f"Saved components figure: {out_png}")


def save_manifest(path: str, extra: Optional[Dict[str, object]] = None) -> None:
    """v7: 実行条件の記録（CFG 全体、依存パッケージの版、日時、環境）。"""
    import json, platform, datetime, importlib.metadata as _md
    vers = {}
    for pkg in ("numpy", "scipy", "stim", "pymatching", "numba", "pandas", "matplotlib", "jax"):
        try:
            vers[pkg] = _md.version(pkg)
        except Exception:  # noqa: BLE001
            vers[pkg] = None
    rec = dict(code_version=str(globals().get("CODE_VERSION", "d4_v9_1")), datetime=datetime.datetime.now().isoformat(), python=platform.python_version(),
               platform=platform.platform(), versions=vers, CFG={k: (v if isinstance(v, (int, float, str, bool, type(None), list, dict)) else str(v))
                                                                  for k, v in CFG.items()})
    if "VCFG" in globals():
        rec["VCFG"] = {k: (v if isinstance(v, (int, float, str, bool, type(None), list, dict)) else str(v)) for k, v in VCFG.items()}
    if extra:
        rec.update(extra)
    with open(path, "w") as fh:
        json.dump(rec, fh, indent=2, ensure_ascii=False, default=str)
    print(f"Saved manifest: {path}")


def run_production(noise_models: Optional[Sequence[str]] = None, treatments: Optional[Sequence[str]] = None,
                   shots: Optional[int] = None) -> Dict[Tuple[str, str], pd.DataFrame]:
    """v9: 本番の一括実行（R1-2, R1-4, R1-5）。ノイズモデル x dressing の扱い（D4 = exact と対照実験 none,
    kappa_injection）を、同じ L・同じショット数・交点付近の p（PRODUCTION_P_RANGE）で順に実行し、
    最後に対照実験の重ね描き（plot_treatment_comparison）を作る。CFG の他のキーはそのまま使う。"""
    saved = {k: CFG[k] for k in ("noise_model", "dressing_treatment", "p_min", "p_max", "out_csv", "out_png", "shots")}
    out = {}
    try:
        for nm in (noise_models or CFG["production_noise_models"]):
            for tr in (treatments or CFG["production_dressing_treatments"]):
                CFG.update(noise_model=nm, dressing_treatment=tr, out_csv=None, out_png=None)
                if shots is not None:
                    CFG["shots"] = int(shots)
                rng_ = PRODUCTION_P_RANGE.get((nm, tr))
                if nm == "circuit_level" and tr == "exact" and str(CFG.get("circuit_noise_preset")) != "uniform":
                    rng_ = RECOMMENDED_P_RANGE["circuit_level"]
                CFG["p_min"], CFG["p_max"] = (None, None) if rng_ is None else rng_
                print(f"\n########## production: noise_model={nm} dressing_treatment={tr} "
                      f"p=[{CFG['p_min']}, {CFG['p_max']}] shots={CFG['shots']} L={CFG['L_values']} ##########")
                out[(nm, tr)] = run_experiments()
            plot_treatment_comparison(nm)
    finally:
        CFG.update(saved)
    return out


def plot_treatment_comparison(noise_model: str, metric: Optional[str] = None, out_png: Optional[str] = None) -> None:
    """v9: D4（exact）と対照実験（none, kappa_injection）の曲線を、出力フォルダの CSV から重ねて描く（論文の Fig. 4）。"""
    metric = str(metric or CFG.get("failure_metric", "charge"))
    out_dir = str(CFG.get("out_dir") or ".")
    styles = {"exact": ("-o", "D4 (exact)"), "none": ("--s", "no dressing"), "kappa_injection": (":^", "no dressing + r=kappa c p")}
    fig, ax = plt.subplots(figsize=(8, 6))
    palette = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:brown", "tab:purple"]
    found = False
    for tr, (ls, lab) in styles.items():
        tag = f"d4_v9_1_X_memory_{noise_model}_twisted_frame" + ("" if tr == "exact" else f"_{tr}")
        if noise_model == "circuit_level":
            tag += f"_{CFG.get('circuit_noise_preset', 'legacy_v7')}"
        path = os.path.join(out_dir, tag + ".csv")
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        found = True
        for i, L in enumerate(sorted(df["L"].unique())):
            sub = df[df["L"] == L].sort_values("p")
            y = sub[f"ler_{metric}"].where(sub[f"ler_{metric}"] > 0)
            ax.plot(sub["p"], y, ls, ms=4, color=palette[i % len(palette)], label=f"L={int(L)} {lab}")
    if not found:
        print(f"[plot_treatment_comparison] no CSV for {noise_model} in {out_dir}")
        plt.close(fig)
        return
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("physical error rate p")
    ax.set_ylabel(f"logical error rate ({metric})")
    ax.set_title(f"D4 vs control experiments ({noise_model})")
    ax.grid(True, which="both", alpha=0.4)
    ax.legend(fontsize=7, ncol=3)
    fig.tight_layout()
    path = out_png or os.path.join(out_dir, f"d4_v9_1_treatment_comparison_{noise_model}_{metric}.png")
    fig.savefig(path, dpi=160)
    if bool(CFG.get("save_pdf", True)):
        fig.savefig(os.path.splitext(path)[0] + ".pdf")
    plt.close(fig)
    print(f"Saved treatment comparison: {path}")


if __name__ == "__main__":
    results = run_experiments()