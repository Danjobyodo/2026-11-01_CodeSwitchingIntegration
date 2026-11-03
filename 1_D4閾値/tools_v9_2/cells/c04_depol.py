@dataclass(frozen=True)
class DemXArtifacts:
    circuit: "stim.Circuit"
    dem: "stim.DetectorErrorModel"
    n_observables: int
    model_label: str


PhenomenologicalXArtifacts = DemXArtifacts
CircuitLevelXArtifacts = DemXArtifacts
DepolarizingXArtifacts = DemXArtifacts


def _append_mpp_round(
    circuit: "stim.Circuit",
    x_stabs_qubits: Sequence[Sequence[int]],
    meas_p: float,
) -> None:
    targets: List["stim.GateTarget"] = []
    for qubits in x_stabs_qubits:
        for index, q in enumerate(qubits):
            targets.append(stim.target_x(q))
            if index < len(qubits) - 1:
                targets.append(stim.target_combiner())
    if meas_p > 0:
        circuit.append("MPP", targets, meas_p)
    else:
        circuit.append("MPP", targets)


def _pair_channel_probs(mode: str, r: float) -> Optional[List[float]]:
    r = _clip_prob(r)
    if r <= 0:
        return None

    probs = [0.0] * 15
    if mode == "pairwise_graphlike":
        probs[2] = r * (1.0 - r)
        probs[11] = r * (1.0 - r)
        probs[14] = r * r
        return probs
    if mode == "pessimistic_pairwise":
        probs[14] = min(0.499999, 1.5 * r)
        return probs
    raise ValueError(f"Unknown dressing mode: {mode}")


def _resolve_depolarizing_params(
    *,
    p: float,
    dressing_mode: Optional[str],
    data_scale: Optional[float],
    meas_scale: Optional[float],
    dressing_scale: Optional[float],
) -> Dict[str, float | str]:
    mode = str(CFG["depolarizing_dressing_mode"] if dressing_mode is None else dressing_mode)
    data_p = _clip_prob(float(CFG["depolarizing_data_scale"] if data_scale is None else data_scale) * p)
    meas_p = _clip_prob(float(CFG["depolarizing_meas_scale"] if meas_scale is None else meas_scale) * p)
    dress_scale = max(
        0.0,
        float(CFG["depolarizing_dressing_scale"] if dressing_scale is None else dressing_scale),
    )
    return {
        "dressing_mode": mode,
        "data_p": data_p,
        "meas_p": meas_p,
        "dressing_scale": dress_scale,
    }


def build_depolarizing_x_circuit(
    *,
    stab: D4Stabilizers,
    rounds: int,
    p: float,
    data_scale: Optional[float] = None,
    meas_scale: Optional[float] = None,
    dressing_scale: Optional[float] = None,
    dressing_mode: Optional[str] = None,
    final_noise: bool = True,
) -> DepolarizingXArtifacts:
    if stim is None:
        raise RuntimeError("stim is not available.")

    params = _resolve_depolarizing_params(
        p=p,
        dressing_mode=dressing_mode,
        data_scale=data_scale,
        meas_scale=meas_scale,
        dressing_scale=dressing_scale,
    )

    lat = stab.lat
    n_data = 3 * len(lat.edges)
    data = list(range(n_data))
    obs_paths = build_dual_x_observable_paths(lat)
    n_obs = len(obs_paths)
    x_stabs_qubits = build_vertex_x_measurement_supports(stab)
    n_checks = len(x_stabs_qubits)
    pair_events = build_pairwise_dressing_events(stab)
    incidence = build_dressing_qubit_incidence(pair_events)
    circuit = stim.Circuit()
    circuit.append("R", data)
    circuit.append("H", data)

    data_p = float(params["data_p"])
    meas_p = float(params["meas_p"])
    mode = str(params["dressing_mode"])
    base_dressing_rate = float(params["dressing_scale"]) * (2.0 * data_p / 3.0)

    for round_index in range(rounds):
        if data_p > 0:
            circuit.append("DEPOLARIZE1", data, data_p)

        if mode != "off" and base_dressing_rate > 0:
            for event in pair_events:
                q1, q2 = event.qubits
                local_norm = max(incidence.get(q1, 1), incidence.get(q2, 1))
                pair_rate = base_dressing_rate * event.multiplicity / max(1, local_norm)
                probs = _pair_channel_probs(mode, pair_rate)
                if probs is not None:
                    circuit.append("PAULI_CHANNEL_2", [q1, q2], probs)

        _append_mpp_round(circuit, x_stabs_qubits, meas_p=meas_p)

        if round_index == 0:
            for check_index in range(n_checks):
                cur = stim.target_rec(-(n_checks - check_index))
                circuit.append("DETECTOR", [cur])
        else:
            for check_index in range(n_checks):
                cur = stim.target_rec(-(n_checks - check_index))
                prev = stim.target_rec(-(2 * n_checks - check_index))
                circuit.append("DETECTOR", [cur, prev])

    if final_noise and data_p > 0:  # v6: final_noise=False -> noiseless final readout (= perfect final round)
        circuit.append("DEPOLARIZE1", data, data_p)
    if final_noise and meas_p > 0:
        circuit.append("Z_ERROR", data, meas_p)

    circuit.append("H", data)
    circuit.append("M", data)

    for check_index, qubits in enumerate(x_stabs_qubits):
        last_mpp = stim.target_rec(-(n_data + n_checks - check_index))
        recs = [stim.target_rec(-(n_data - q)) for q in qubits]
        circuit.append("DETECTOR", [last_mpp] + recs)

    for observable_index, path in enumerate(obs_paths):
        targets = [stim.target_rec(-(n_data - q)) for q in path]
        circuit.append("OBSERVABLE_INCLUDE", targets, observable_index)

    dem = circuit.detector_error_model(
        decompose_errors=True,
        approximate_disjoint_errors=True,
    )
    return DepolarizingXArtifacts(
        circuit=circuit,
        dem=dem,
        n_observables=n_obs,
        model_label="depolarizing_surrogate_v2",
    )


def build_depolarizing_approx_baseline_circuit(
    *,
    stab: D4Stabilizers,
    rounds: int,
    p: float,
    data_scale: float = 1.0,
    meas_scale: float = 1.0,
    kickback_scale: float = 1.0,
) -> DepolarizingXArtifacts:
    if stim is None:
        raise RuntimeError("stim is not available.")

    lat = stab.lat
    n_data = 3 * len(lat.edges)
    data = list(range(n_data))
    obs_paths = build_dual_x_observable_paths(lat)
    x_stabs_qubits = build_vertex_x_measurement_supports(stab)
    pair_events = build_pairwise_dressing_events(stab)

    data_p = _clip_prob(data_scale * p)
    meas_p = _clip_prob(meas_scale * p)
    r_xy = _clip_prob(kickback_scale * (2.0 * data_p / 3.0))
    kick_probs = [0.0] * 15
    if r_xy > 0:
        kick_probs[2] = r_xy * (1.0 - r_xy)
        kick_probs[11] = r_xy * (1.0 - r_xy)
        kick_probs[14] = r_xy * r_xy

    circuit = stim.Circuit()
    circuit.append("R", data)
    circuit.append("H", data)

    n_checks = len(x_stabs_qubits)
    for round_index in range(rounds):
        if data_p > 0:
            circuit.append("DEPOLARIZE1", data, data_p)
        if r_xy > 0:
            for event in pair_events:
                circuit.append("PAULI_CHANNEL_2", list(event.qubits), kick_probs)
        _append_mpp_round(circuit, x_stabs_qubits, meas_p=meas_p)
        if round_index == 0:
            for check_index in range(n_checks):
                cur = stim.target_rec(-(n_checks - check_index))
                circuit.append("DETECTOR", [cur])
        else:
            for check_index in range(n_checks):
                cur = stim.target_rec(-(n_checks - check_index))
                prev = stim.target_rec(-(2 * n_checks - check_index))
                circuit.append("DETECTOR", [cur, prev])

    if data_p > 0:
        circuit.append("DEPOLARIZE1", data, data_p)
    if meas_p > 0:
        circuit.append("Z_ERROR", data, meas_p)
    circuit.append("H", data)
    circuit.append("M", data)

    for check_index, qubits in enumerate(x_stabs_qubits):
        last_mpp = stim.target_rec(-(n_data + n_checks - check_index))
        recs = [stim.target_rec(-(n_data - q)) for q in qubits]
        circuit.append("DETECTOR", [last_mpp] + recs)

    for observable_index, path in enumerate(obs_paths):
        targets = [stim.target_rec(-(n_data - q)) for q in path]
        circuit.append("OBSERVABLE_INCLUDE", targets, observable_index)

    dem = circuit.detector_error_model(
        decompose_errors=True,
        approximate_disjoint_errors=True,
    )
    return DepolarizingXArtifacts(
        circuit=circuit,
        dem=dem,
        n_observables=len(obs_paths),
        model_label="depolarizing_approx_baseline",
    )