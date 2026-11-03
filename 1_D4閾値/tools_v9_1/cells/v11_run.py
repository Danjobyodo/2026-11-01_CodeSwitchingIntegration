def build_validation_context(noise_model: str, p: float, logical_colors: Optional[str] = None):
    """L=3 の検証に必要な部品（幾何・JIT・終端処理・故障表）をまとめて作る（D4 = dressing_treatment "exact"）。"""
    L = int(VCFG["L"])
    CFG["dressing_treatment"] = "exact"
    CFG["logical_colors"] = str(VCFG["logical_colors"] if logical_colors is None else logical_colors)
    stab, g = _tf_geometry_cached(L, CFG["logical_colors"])
    nz = resolve_tf_noise(noise_model, p, L)
    w_s, w_t = _jit_weights(nz)
    jit = JITFluxDecoder(g, int(nz["rounds"]), w_s, w_t, float(CFG["jit_boundary_offset"]),
                         future_boundary=_jit_future_boundary(nz))   # v9: メインと同じ未来境界の扱い
    closer = FluxCloser(g)
    col_rank = {COLORS.index(c): i for i, c in enumerate(str(CFG["x_check_order"]))}
    order = np.array(sorted(range(len(stab.vertex_X)), key=lambda ci: (col_rank[int(g.chk_color[ci])], int(g.chk_vertex[ci]))), np.int32)
    xt = zt = None
    if nz["kind"] == "circuit":
        xt = build_xcheck_fault_table(nz["params"])
        zt = build_zcheck_fault_table(nz["params"])
    return dict(L=L, stab=stab, g=g, nz=nz, jit=jit, closer=closer, order=order, xt=xt, zt=zt)


def lockstep_exactness_test(noise_model: str, p: float, shots: int, seed: int, dense: "DenseBackend",
                            logical_colors: str) -> Dict[str, float]:
    """(B) twisted-frame が結果を決め、密な厳密計算がその結果の確率を独立に計算して照合する。
    検査した軌道上の全ての dressed X チェック測定（CL はゲート単位の故障込み）の確率と、終状態の論理忠実度を比較。"""
    ctx = build_validation_context(noise_model, p, logical_colors)
    g, stab = ctx["g"], ctx["stab"]
    tf = TFBackend(g, stab, ctx["xt"], ctx["zt"])
    rng = np.random.default_rng(seed)
    nh = len(g.hol_coords)
    max_pdev = 0.0
    max_fdev = 0.0
    n_rand = 0
    n_ok = 0
    t0 = time.time()
    for s in range(shots):
        st0 = tf.st.stats.copy()
        r = protocol_shot([tf, dense], g, stab, ctx["nz"], ctx["jit"], ctx["closer"], ctx["order"], rng,
                          tol=float(VCFG["lockstep_tol"]), xtab=ctx["xt"], ztab=ctx["zt"])
        max_pdev = max(max_pdev, r["maxdev"])
        n_rand += int((tf.st.stats[1] - st0[1]) + (tf.st.stats[2] - st0[2]))
        if not r["flux_fail"]:
            n_ok += 1
            for trial in range(1 << nh):
                delta = [(trial >> i) & 1 for i in range(nh)]
                max_fdev = max(max_fdev, abs(logical_fidelity(r["finals"]["twisted_frame"], delta, nh)
                                             - logical_fidelity(r["finals"]["dense"], delta, nh)))
    out = dict(noise_model=noise_model, logical_colors=logical_colors, p=p, shots=shots, max_prob_deviation=max_pdev,
               max_fidelity_deviation=max_fdev, shots_compared_fidelity=n_ok,
               random_outcomes_checked=n_rand, seconds=time.time() - t0)
    if max_pdev > float(VCFG["lockstep_tol"]) or max_fdev > 1e-3:
        raise AssertionError(f"exactness test FAILED: {out}")
    return out


def _rates_from_counts(n_charge: int, n_flux: int, shots: int) -> Dict[str, float]:
    alpha = 1.0 - float(CFG["confidence_level"])
    out = {}
    for key, (k, n) in _metric_counts(n_charge, n_flux, n_charge + n_flux, shots).items():
        _, lo, hi = calc_agresti_coull_interval(max(n, 0), k, alpha)
        out.update({f"n_fail_{key}": k, f"n_trials_{key}": n, f"ler_{key}": (k / n if n > 0 else float("nan")),
                    f"ler_{key}_lower": lo, f"ler_{key}_upper": hi})
    return out


def dense_exact_ler_point(noise_model: str, p: float, shots: int, seed: int, dense: "DenseBackend") -> Dict[str, float]:
    """(C) 密な厳密シミュレーション単独で記憶実験を行い、同じ復号器・同じ失敗判定で LER を求める。"""
    ctx = build_validation_context(noise_model, p)
    g, stab = ctx["g"], ctx["stab"]
    rng = np.random.default_rng(seed)
    R = int(ctx["nz"]["rounds"])
    dem = _charge_decoder_dem(noise_model, stab, R, p)
    matcher = pymatching.Matching.from_detector_error_model(dem)
    nh = len(g.hol_coords)
    n_charge = n_flux = 0
    t0 = time.time()
    for s in range(shots):
        r = protocol_shot([dense], g, stab, ctx["nz"], ctx["jit"], ctx["closer"], ctx["order"], rng,
                          xtab=ctx["xt"], ztab=ctx["zt"])
        if r["flux_fail"]:
            n_flux += 1
            continue
        pred = np.asarray(matcher.decode(r["dets"]), dtype=np.uint8)
        delta = [int(pred[2 * int(g.hol_colors[hi])]) ^ int(r["par"][hi]) for hi in range(nh)]
        F = logical_fidelity(r["finals"]["dense"], delta, nh)
        if rng.random() < 1.0 - F:
            n_charge += 1
    out = dict(model="exact_dense", kappa=float("nan"), p=p, shots=shots, seed=seed, seconds=time.time() - t0)
    out.update(_rates_from_counts(n_charge, n_flux, shots))
    return out


def tf_engine_ler_point(noise_model: str, p: float, shots: int) -> Dict[str, float]:
    """(C) メインコードと全く同じ経路（run_one_point_tf）で L=3 の LER を求める。"""
    CFG["dressing_treatment"] = "exact"
    CFG["logical_colors"] = str(VCFG["logical_colors"])
    t0 = time.time()
    r = run_one_point_tf(L=int(VCFG["L"]), p=p, shots=shots, noise_model=noise_model)
    out = dict(model="twisted_frame_main", kappa=decoder_kappa(noise_model), p=p, shots=shots, seed=r["seed"],
               seconds=time.time() - t0)
    for key in METRIC_KEYS:
        for suf in ("", "_lower", "_upper"):
            out[f"ler_{key}{suf}"] = r[f"ler_{key}{suf}"]
        out[f"n_fail_{key}"] = int(r[f"n_fail_{key}"])
        out[f"n_trials_{key}"] = int(r[f"n_trials_{key}"])
    return out


def old_surrogate_ler_point(noise_model: str, p: float, shots: int, kappa: float, seed: int) -> Dict[str, float]:
    """(C, 参考) 旧研究のサロゲート（|+>^n から bare X を MPP 測定 + dressed ペアに r=κcp の Z 注入, Stim）を
    κ を変えて評価する。初期状態・終端・雑音の集約・失敗判定（選んだ色の x 方向 bare 観測量の誤り）が厳密側と異なる
    「別モデルの参考比較」であり、非可換性の効果だけを切り分けた比較ではない（切り分けはメインの dressing_treatment で行う）。"""
    L = int(VCFG["L"])
    model = _resolve_noise_model_name(noise_model)
    stab = build_d4_stabilizers(TriangulatedTorus.build(L))
    R = _resolve_rounds(model, L)
    if model == "depolarizing_surrogate_v2":
        arts = build_depolarizing_x_circuit(stab=stab, rounds=R, p=p, dressing_scale=kappa)
    elif model == "phenomenological":
        arts = build_phenomenological_x_circuit(stab=stab, rounds=R, p=p, kickback_scale=kappa)
    else:
        arts = build_circuit_level_x_circuit(stab=stab, rounds=R, p=p, kickback_scale=kappa)
    matcher = pymatching.Matching.from_detector_error_model(arts.dem)
    sampler = arts.circuit.compile_detector_sampler(seed=seed)
    dets, obs = sampler.sample(shots, separate_observables=True)
    pred = _decode_observables(matcher, dets, arts.n_observables)
    cols = [2 * COLORS.index(c) for c in str(VCFG["logical_colors"])]
    fails = np.any(pred[:, cols] != obs[:, cols], axis=1)
    n = int(fails.sum())
    alpha = 1.0 - float(CFG["confidence_level"])
    _, lo, hi = calc_agresti_coull_interval(shots, n, alpha)
    out = dict(model="old_surrogate", kappa=float(kappa), p=p, shots=shots, seed=seed, seconds=float("nan"))
    for key in METRIC_KEYS:  # 旧モデルには flux 側がないので、全ての列に同じ値を入れる（作図用）
        out.update({f"n_fail_{key}": n, f"n_trials_{key}": shots, f"ler_{key}": n / shots,
                    f"ler_{key}_lower": lo, f"ler_{key}_upper": hi})
    return out


def decoder_kappa_scan(noise_model: str) -> pd.DataFrame:
    """(D, 任意) 電荷デコーダの事前分布 κ_dec の調整。
    物理は厳密（twisted-frame）なので、ここで変わるのは復号器だけ。最大の L で charge 指標の LER が最小になる κ を
    メイン Cell 2 の tf_decoder_kappa[noise_model] に設定する。L=3 以外も使うが、これは正当化ではなく復号器の調整。
    本番の閾値推定とは別の乱数（seed）で行うこと（CFG["seed"] を変えてから実行する）。"""
    saved = CFG["tf_decoder_kappa"]
    CFG["dressing_treatment"] = "exact"
    CFG["logical_colors"] = str(VCFG["decoder_scan_logical_colors"])
    p = float(VCFG["decoder_scan_p"][noise_model])
    rows = []
    try:
        for kap in VCFG["decoder_scan_kappas"][noise_model]:
            CFG["tf_decoder_kappa"] = float(kap)
            for L in VCFG["decoder_scan_L"]:
                r = run_one_point_tf(L=int(L), p=p, shots=int(VCFG["decoder_scan_shots"]), noise_model=noise_model)
                rows.append(dict(noise_model=noise_model, p=p, kappa_dec=float(kap), L=int(L),
                                 ler_charge=r["ler_charge"], ler_charge_lower=r["ler_charge_lower"],
                                 ler_charge_upper=r["ler_charge_upper"]))
                print(f"(D) {noise_model} p={p:g} kappa_dec={kap:g} L={L}: charge LER={r['ler_charge']:.4f} "
                      f"[{r['ler_charge_lower']:.4f},{r['ler_charge_upper']:.4f}]", flush=True)
    finally:
        CFG["tf_decoder_kappa"] = saved
        CFG["logical_colors"] = str(VCFG["logical_colors"])
    df = pd.DataFrame(rows)
    Lmax = max(int(L) for L in VCFG["decoder_scan_L"])
    best = df[df.L == Lmax].sort_values("ler_charge").iloc[0]
    print(f"(D) recommended tf_decoder_kappa[{noise_model!r}] = {best.kappa_dec:g} (lowest charge LER at L={Lmax}). "
          "差が誤差棒（95% 区間）より小さい場合は既定値のままでよい。")
    df.to_csv(os.path.join(str(VCFG.get("out_dir") or "."), f"d4_v9_1_decoder_kappa_scan_{noise_model}.csv"), index=False)
    return df


def _two_proportion_z(k1, n1, k2, n2):
    if n1 <= 0 or n2 <= 0:
        return 0.0
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(max(p * (1 - p) * (1 / n1 + 1 / n2), 1e-300))
    return (k1 / n1 - k2 / n2) / se if se > 0 else 0.0


def plot_validation(df: pd.DataFrame, noise_model: str, out_png: str, metric: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    style = {
        "exact_dense": dict(color="tab:red", marker="s", linestyle="--", label="Exact (dense state vector)"),
        "twisted_frame_main": dict(color="tab:blue", marker="o", linestyle="-", label="Twisted-frame sampler (main code)"),
    }
    for model, st in style.items():
        sub = df[df["model"] == model].sort_values("p")
        if sub.empty:
            continue
        x = sub["p"].to_numpy()
        y = np.maximum(sub[f"ler_{metric}"].to_numpy(), 1e-10)
        ax.errorbar(x, y, yerr=[np.maximum(0, y - sub[f"ler_{metric}_lower"].to_numpy()),
                                np.maximum(0, sub[f"ler_{metric}_upper"].to_numpy() - y)],
                    fmt=st["marker"], linestyle=st["linestyle"], color=st["color"], label=st["label"], capsize=4, alpha=0.85)
    old = df[df["model"] == "old_surrogate"]
    greys = plt.cm.Greys(np.linspace(0.35, 0.8, max(1, old["kappa"].nunique())))
    for i, (kap, sub) in enumerate(old.groupby("kappa")):
        sub = sub.sort_values("p")
        ax.plot(sub["p"], np.maximum(sub[f"ler_{metric}"], 1e-10), marker="^", linestyle=":", color=greys[i],
                label=f"Previous surrogate r=κcp (κ={kap:g}, own metric)", alpha=0.9)
    display = {"depolarizing": "Depolarizing (code capacity)", "phenomenological": "Phenomenological", "circuit_level": "Circuit-level"}
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"Physical error rate $p$", fontsize=20)
    ax.set_ylabel({"charge": r"$P_L$ (charge, flux-success shots)", "combined": r"$P_L$ (charge or flux)",
                   "flux": r"$P_L$ (flux)"}[metric], fontsize=18)
    ax.set_title(display.get(noise_model, noise_model), fontsize=26, fontweight="bold", pad=14)
    ax.tick_params(axis="both", which="major", labelsize=16)
    ax.text(0.02, 0.98, f"L={VCFG['L']}, logical colors={VCFG['logical_colors']}", transform=ax.transAxes,
            ha="left", va="top", fontsize=11, alpha=0.6)
    ax.grid(True, which="major", alpha=0.7)
    ax.grid(True, which="minor", linestyle=":", alpha=0.3)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    print(f"Saved PNG: {out_png}")
    if bool(VCFG.get("save_pdf", True)):
        fig.savefig(os.path.splitext(out_png)[0] + ".pdf")


def _ler_section(noise_model: str, lc: str, stab, out_csv: str, out_png: str) -> pd.DataFrame:
    """(C) 独立標本の論理誤り率の比較を、論理セクター lc（"r" または "rgb"）で行う。"""
    VCFG["logical_colors"] = lc
    CFG["logical_colors"] = lc
    _, g = _tf_geometry_cached(int(VCFG["L"]), lc)
    t0 = time.time()
    dense = DenseBackend(g, stab)
    print(f"(C) [{lc}] dense reference: k={g.k}, 2^k={1 << g.k} amplitudes ({time.time() - t0:.1f}s)")
    rows = []
    p_values = [float(x) for x in VCFG["p_values"][noise_model]]
    for i, p in enumerate(p_values):
        r_ex = dense_exact_ler_point(noise_model, p, int(VCFG["shots_exact"]), int(CFG["seed"]) + 101 * i + 1, dense)
        r_ex["logical_colors"] = lc
        rows.append(r_ex)
        r_tf = tf_engine_ler_point(noise_model, p, int(VCFG["shots_tf"]))
        r_tf["logical_colors"] = lc
        rows.append(r_tf)
        msg = []
        for key in ("charge", "combined"):
            z = _two_proportion_z(r_ex[f"n_fail_{key}"], r_ex[f"n_trials_{key}"], r_tf[f"n_fail_{key}"], r_tf[f"n_trials_{key}"])
            msg.append(f"{key}: exact {r_ex[f'ler_{key}']:.4f} / main {r_tf[f'ler_{key}']:.4f} (z={z:+.2f})")
        print(f"(C) [{lc}] p={p:.4e} [{r_ex['seconds']:.0f}s]  " + " | ".join(msg), flush=True)
        if bool(VCFG.get("run_old_surrogate", True)):
            for kap in VCFG["old_kappa_sweep"][noise_model]:
                rr = old_surrogate_ler_point(noise_model, p, int(VCFG["shots_surrogate"]), float(kap), int(CFG["seed"]) + i)
                rr["logical_colors"] = lc
                rows.append(rr)
        pd.DataFrame(rows).to_csv(out_csv, index=False)
    del dense
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"Saved CSV: {out_csv}")
    ex = df[df.model == "exact_dense"].set_index("p")
    tfm = df[df.model == "twisted_frame_main"].set_index("p")
    for key in ("charge", "combined"):
        zs = [_two_proportion_z(ex.loc[p, f"n_fail_{key}"], ex.loc[p, f"n_trials_{key}"],
                                tfm.loc[p, f"n_fail_{key}"], tfm.loc[p, f"n_trials_{key}"]) for p in ex.index]
        chi2 = float(np.sum(np.square(zs)))
        try:
            from scipy.stats import chi2 as _chi2
            pval = float(_chi2.sf(chi2, len(zs)))
        except Exception:  # noqa: BLE001
            pval = float("nan")
        print(f"[summary/{key}/{lc}] exact vs main engine: z={['%+.2f' % z for z in zs]}, sum z^2={chi2:.2f} "
              f"(dof={len(zs)}, upper-tail p={pval:.3f}; 3 モデル x 2 セクターの多重比較に注意)")
    plot_validation(df, noise_model, out_png, str(VCFG.get("compare_metric", "charge")))
    return df


def run_validation() -> pd.DataFrame:
    noise_model = str(VCFG["noise_model"])
    CFG["noise_model"] = noise_model
    CFG["dressing_treatment"] = "exact"
    ler_lcs = list(VCFG.get("ler_logical_colors") or [VCFG["logical_colors"]])
    print(f"[v9 validation] noise_model={noise_model} L={VCFG['L']} (C) logical_colors={ler_lcs} "
          f"circuit_noise_preset={CFG.get('circuit_noise_preset')} jax devices={jax.devices() if JAX_AVAILABLE else None}")
    tag = f"d4_v9_1_validation_L3_{noise_model}"
    if noise_model == "circuit_level":
        tag += f"_{CFG.get('circuit_noise_preset', 'legacy_v7')}"
    out_dir = str(VCFG.get("out_dir") or ".")
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.join(out_dir, tag)
    if bool(CFG.get("save_manifest", True)):
        save_manifest(base + "_manifest.json")
    # (A) geometry
    lat = TriangulatedTorus.build(int(VCFG["L"]))
    stab = build_d4_stabilizers(lat)
    op_nc, flat_nc = count_noncommuting_x_check_pairs(stab)
    print(f"(A) dressed X-check pairs: operator-level noncommuting={op_nc}, noncommuting on flat subspace={flat_nc} (must be 0)")
    if flat_nc:
        raise AssertionError("geometry error")
    # (B) exactness (lockstep) for each logical-sector family
    if bool(VCFG["run_lockstep_test"]):
        lres = []
        for lc in VCFG["lockstep_logical_colors"]:
            _, g_lc = _tf_geometry_cached(int(VCFG["L"]), lc)
            t0 = time.time()
            dense_lc = DenseBackend(g_lc, stab)
            print(f"    dense reference [{lc}]: k={g_lc.k}, 2^k={1 << g_lc.k} amplitudes, initial code state verified in {time.time() - t0:.1f}s")
            res = lockstep_exactness_test(noise_model, float(VCFG["lockstep_p"][noise_model]),
                                          int(VCFG["lockstep_shots"][lc]), int(CFG["seed"]) + 5, dense_lc, lc)
            print(f"(B) lockstep exactness test PASSED [{lc}]: {res}")
            lres.append(res)
            del dense_lc
        pd.DataFrame(lres).to_csv(base + "_lockstep.csv", index=False)
    # (C) LER curves for each logical-sector family (v9: "r" と、メインの本番と同じ "rgb"。R1-6)
    dfs = []
    for lc in ler_lcs:
        dfs.append(_ler_section(noise_model, lc, stab, base + f"_C_{lc}.csv", base + f"_C_{lc}.png"))
    VCFG["logical_colors"] = ler_lcs[0]
    if bool(VCFG.get("run_decoder_kappa_scan", False)):
        decoder_kappa_scan(noise_model)
    return pd.concat(dfs, ignore_index=True)

if __name__ == "__main__":
    vresults = {}
    for _m in VCFG["noise_models"]:
        VCFG["noise_model"] = _m
        vresults[_m] = run_validation()