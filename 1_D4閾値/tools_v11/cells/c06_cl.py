def _effective_per_qubit_round_p(params: Dict[str, float]) -> float:
    """各 data qubit に毎ラウンド掛ける DEPOLARIZE1 の effective レート。

    D4 (L=3) の標準位相で 1 data qubit は 1 round あたり ≈ 4 CX を浴びる
    (ancilla との CX 1 個 + CCZ 分解の内側 CX ~3 個)。DEPOLARIZE2 の片側
    marginal を `2 × twoq_p / 3` とみなして count 倍し、idle / 1q と独立合算する。
    最終的な係数のズレは pair-channel 側の `circuit_kickback_scale` で吸収する。

    v9 の注（Gemini の指摘 1.1(3)）: DEPOLARIZE2(p) の片側の量子ビットが恒等でない確率は正確には 12/15 p = 4/5 p
    （X 成分または Z 成分を持つ確率はそれぞれ 8/15 p）で、ここの 2/3 p は旧研究の近似式である。旧研究のサロゲート
    （engine="stim_surrogate"、cl_decoder_prior="legacy"）を再現するためだけに残しており、値は変えない。
    v9 の本番（twisted_frame エンジン）はこの関数を使わない。
    """
    cx_per_round = 4
    r_2q_marginal = _clip_prob((2.0 / 3.0) * float(params["twoq_p"])) * cx_per_round
    return _combine_independent_probabilities(
        float(params["idle_p"]),
        float(params["oneq_p"]),
        r_2q_marginal,
    )


def _circuit_level_pair_kickback_rate(
    params: Dict[str, float],
    multiplicity: int,
    kickback_scale: float,
) -> float:
    """CZ ペアあたりの graphlike Z kickback レート。

    CCZ 1 個あたり pair member に届く Z は:
      * CCZ 分解内の CX 起因 ≈ twoq_p
      * 内側の T/T_DAG (q1, q2 を触る ~3 個) 起因 ≈ 3 × noncliff_p
    multiplicity = この unique pair が 1 round で CCZ 測定に登場する回数。
    """
    per_ccz = float(params["twoq_p"]) + 3.0 * float(params["noncliff_p"])
    return _clip_prob(kickback_scale * multiplicity * per_ccz)


def build_circuit_level_x_circuit(
    *,
    stab: D4Stabilizers,
    rounds: int,
    p: float,
    final_noise: bool = True,
    kickback_scale: Optional[float] = None,
) -> CircuitLevelXArtifacts:
    """Circuit-level effective surrogate (MPP ベース)。

    Tsim 厳密 (CCZ ベース測定回路 + ゲート粒度の circuit-level noise) と
    『2026-05-22_Tsimでsurrogateを正当化(circuit_level).py』で per-check round-1
    XOR detector の発火率を照合し、最適 `circuit_kickback_scale` を確定する。
    確定後はその値を Cell 2 の CFG に反映するだけで surrogate が正当化される。
    """
    if stim is None:
        raise RuntimeError("stim is not available.")

    params = _resolve_circuit_level_params(p, preset="legacy_v7")  # 旧研究のサロゲートは常に v7 の定義
    if kickback_scale is None:  # v6: override は正当化コードの κ 掃引・v6 デコーダ事前分布用
        kickback_scale = float(CFG.get("circuit_kickback_scale", 1.0))
    kickback_scale = float(kickback_scale)

    lat = stab.lat
    n_data = 3 * len(lat.edges)
    data = list(range(n_data))
    obs_paths = build_dual_x_observable_paths(lat)
    x_stabs_qubits = build_vertex_x_measurement_supports(stab)
    n_checks = len(x_stabs_qubits)
    pair_events = build_pairwise_dressing_events(stab)

    r_data_round = _effective_per_qubit_round_p(params)
    r_meas = float(params["meas_p"])
    r_init_data = _combine_independent_probabilities(
        float(params["init_p"]), float(params["oneq_p"]),
    )
    r_final_pre = _combine_independent_probabilities(
        float(params["idle_p"]), float(params["meas_p"]),
    )

    circuit = stim.Circuit()
    circuit.append("R", data)
    if r_init_data > 0:
        circuit.append("DEPOLARIZE1", data, r_init_data)
    circuit.append("H", data)

    for round_index in range(rounds):
        if r_data_round > 0:
            circuit.append("DEPOLARIZE1", data, r_data_round)

        for ev in pair_events:
            q1, q2 = ev.qubits
            r = _circuit_level_pair_kickback_rate(
                params, ev.multiplicity, kickback_scale,
            )
            if r > 0:
                probs = [0.0] * 15
                probs[2] = r * (1.0 - r)   # IZ
                probs[11] = r * (1.0 - r)  # ZI
                probs[14] = r * r          # ZZ
                circuit.append("PAULI_CHANNEL_2", [q1, q2], probs)

        _append_mpp_round(circuit, x_stabs_qubits, meas_p=r_meas)
        _append_detector_layout(circuit, round_index=round_index, n_checks=n_checks)

    if final_noise and r_final_pre > 0:  # v6: final_noise=False -> perfect final round
        circuit.append("DEPOLARIZE1", data, r_final_pre)
    if final_noise and float(params["meas_p"]) > 0:
        circuit.append("Z_ERROR", data, float(params["meas_p"]))
    circuit.append("H", data)
    circuit.append("M", data)

    _append_final_readout_layout(
        circuit,
        x_stabs_qubits=x_stabs_qubits,
        obs_paths=obs_paths,
        n_data=n_data,
    )

    dem = circuit.detector_error_model(
        decompose_errors=True,
        approximate_disjoint_errors=True,
    )

    return CircuitLevelXArtifacts(
        circuit=circuit,
        dem=dem,
        n_observables=len(obs_paths),
        model_label="circuit_level_validated_surrogate_v1",
    )