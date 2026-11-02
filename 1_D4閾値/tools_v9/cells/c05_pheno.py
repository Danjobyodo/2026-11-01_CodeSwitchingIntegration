@dataclass(frozen=True)
class NonCliffordInteractionSite:
    pair_qubits: Tuple[int, int]
    anchor_qubit: int


@dataclass(frozen=True)
class CircuitLevelCheckSchedule:
    check_index: int
    color: Color
    vertex: Vertex
    x_qubits: Tuple[int, ...]
    noncliff_sites: Tuple[NonCliffordInteractionSite, ...]


@dataclass(frozen=True)
class EffectiveFaultEvent:
    location_kind: str
    source_check: int
    probability: float
    pauli_targets: Tuple[Tuple[str, int], ...]
    touched_checks: Tuple[int, ...]
    touched_observables: Tuple[int, ...]
    graphlike: bool
    explanation: str


@dataclass(frozen=True)
class CircuitLevelSchedule:
    n_data: int
    obs_paths: List[List[int]]
    x_stabs_qubits: List[List[int]]
    check_schedules: Tuple[CircuitLevelCheckSchedule, ...]
    qubit_to_checks: Dict[int, Tuple[int, ...]]
    qubit_to_observables: Dict[int, Tuple[int, ...]]


@dataclass(frozen=True)
class CircuitLevelNoiseSummary:
    prep_depolarize_p: float
    round_depolarize_p: Dict[int, float]
    tail_depolarize_p: Dict[int, float]
    single_noncliff_channels: Dict[int, Tuple[float, float, float]]
    correlated_events: Tuple[EffectiveFaultEvent, ...]
    meas_flip_p: float
    final_readout_flip_p: float
    model_label: str


def _combine_independent_probabilities(*rates: float, upper: float = 0.499999) -> float:
    keep = 1.0
    for rate in rates:
        clipped = min(0.999999, max(0.0, float(rate)))
        keep *= 1.0 - clipped
    return min(upper, max(0.0, 1.0 - keep))


def _build_qubit_incidence_map(
    supports: Sequence[Sequence[int]],
) -> Dict[int, Tuple[int, ...]]:
    out: Dict[int, List[int]] = {}
    for index, qubits in enumerate(supports):
        for q in qubits:
            out.setdefault(q, []).append(index)
    return {q: tuple(indices) for q, indices in out.items()}


def build_circuit_level_schedule(stab: D4Stabilizers) -> CircuitLevelSchedule:
    lat = stab.lat
    x_stabs_qubits = build_vertex_x_measurement_supports(stab)
    obs_paths = build_dual_x_observable_paths(lat)
    qubit_to_checks = _build_qubit_incidence_map(x_stabs_qubits)
    qubit_to_observables = _build_qubit_incidence_map(obs_paths)

    check_schedules: List[CircuitLevelCheckSchedule] = []
    for check_index, v_stab in enumerate(stab.vertex_X):
        sites: List[NonCliffordInteractionSite] = []
        for edge1, edge2 in v_stab.cz_edge_pairs:
            sites.append(
                NonCliffordInteractionSite(
                    pair_qubits=(
                        edge_color_to_qubit(edge1, v_stab.cz_colors[0]),
                        edge_color_to_qubit(edge2, v_stab.cz_colors[1]),
                    ),
                    anchor_qubit=edge_color_to_qubit(edge1, v_stab.color),
                )
            )
        check_schedules.append(
            CircuitLevelCheckSchedule(
                check_index=check_index,
                color=v_stab.color,
                vertex=v_stab.vertex,
                x_qubits=tuple(x_stabs_qubits[check_index]),
                noncliff_sites=tuple(sites),
            )
        )

    return CircuitLevelSchedule(
        n_data=3 * len(lat.edges),
        obs_paths=obs_paths,
        x_stabs_qubits=x_stabs_qubits,
        check_schedules=tuple(check_schedules),
        qubit_to_checks=qubit_to_checks,
        qubit_to_observables=qubit_to_observables,
    )


def _resolve_circuit_level_params(p: float, preset: Optional[str] = None) -> Dict[str, object]:
    """回路レベル雑音のパラメータ。v9: preset（None なら CFG["circuit_noise_preset"]）で定義を選ぶ。
      "uniform"  : 研究 3 のシナリオ B（Takada et al. App. A2）と同じ。全てのゲートの後に脱分極 p（CCZ は D3(p)）、
                   準備の後・測定の前に反転 p、アイドル雑音なし、H は準備・測定の一部、JIT の X 補正は雑音なし。
      "legacy_v7": v7 と同じ（CFG の circuit_*_scale）。旧研究のサロゲート（engine="stim_surrogate"）は常にこれを使う。
    corr_p は JIT の X 補正ゲートの後の DEPOLARIZE1 の確率（legacy_v7 では oneq_p と同じ）。"""
    preset = str(CFG.get("circuit_noise_preset", "legacy_v7") if preset is None else preset)
    if preset == "uniform":
        q = _clip_prob(p)
        return {"preset": "uniform", "init_p": q, "oneq_p": 0.0, "twoq_p": q, "noncliff_p": q,
                "idle_p": 0.0, "meas_p": q, "corr_p": 0.0}
    if preset != "legacy_v7":
        raise ValueError(f"unknown circuit_noise_preset: {preset}")
    oneq = _clip_prob(float(CFG["circuit_1q_scale"]) * p)
    return {
        "preset": "legacy_v7",
        "init_p": _clip_prob(float(CFG["circuit_init_scale"]) * p),
        "oneq_p": oneq,
        "twoq_p": _clip_prob(float(CFG["circuit_2q_scale"]) * p),
        "noncliff_p": _clip_prob(float(CFG["circuit_noncliff_scale"]) * p),
        "idle_p": _clip_prob(float(CFG["circuit_idle_scale"]) * p),
        "meas_p": _clip_prob(float(CFG["circuit_meas_scale"]) * p),
        "corr_p": oneq,
    }


def _make_fault_event(
    *,
    schedule: CircuitLevelSchedule,
    source_check: int,
    location_kind: str,
    probability: float,
    pauli_targets: Sequence[Tuple[str, int]],
    explanation: str,
) -> EffectiveFaultEvent:
    touched_checks = set()
    touched_observables = set()
    for axis, qubit in pauli_targets:
        if axis in ("Y", "Z"):
            touched_checks.update(schedule.qubit_to_checks.get(qubit, ()))
            touched_observables.update(schedule.qubit_to_observables.get(qubit, ()))
    return EffectiveFaultEvent(
        location_kind=location_kind,
        source_check=source_check,
        probability=_clip_prob(probability),
        pauli_targets=tuple(pauli_targets),
        touched_checks=tuple(sorted(touched_checks)),
        touched_observables=tuple(sorted(touched_observables)),
        graphlike=(len(touched_checks) <= 2 and len(touched_observables) <= 1),
        explanation=explanation,
    )


def enumerate_local_fault_events(
    *,
    schedule: CircuitLevelSchedule,
    p: float,
) -> CircuitLevelNoiseSummary:
    params = _resolve_circuit_level_params(p, preset="legacy_v7")
    pair_incidence: Dict[int, int] = {}
    max_check_degree = max((len(v) for v in schedule.qubit_to_checks.values()), default=1)
    for check in schedule.check_schedules:
        for site in check.noncliff_sites:
            q1, q2 = site.pair_qubits
            pair_incidence[q1] = pair_incidence.get(q1, 0) + 1
            pair_incidence[q2] = pair_incidence.get(q2, 0) + 1
    max_pair_degree = max(pair_incidence.values(), default=1)

    prep_depolarize_p = _combine_independent_probabilities(
        params["init_p"],
        params["oneq_p"],
    )

    round_depolarize_p: Dict[int, float] = {}
    tail_depolarize_p: Dict[int, float] = {}
    single_noncliff_channels: Dict[int, Tuple[float, float, float]] = {}

    for q in range(schedule.n_data):
        check_degree = len(schedule.qubit_to_checks.get(q, ()))
        pair_degree = pair_incidence.get(q, 0)
        clifford_round_p = params["twoq_p"] * check_degree / max(1, max_check_degree)
        round_depol = _combine_independent_probabilities(
            params["idle_p"],
            0.5 * params["oneq_p"],
            0.5 * clifford_round_p,
        )
        tail_depol = _combine_independent_probabilities(
            params["idle_p"],
            0.25 * params["oneq_p"],
        )
        if round_depol > 0:
            round_depolarize_p[q] = round_depol
        if tail_depol > 0:
            tail_depolarize_p[q] = tail_depol

        if pair_degree > 0:
            propagated_single_p = _clip_prob(
                0.35 * params["noncliff_p"] * pair_degree / max(1, max_pair_degree)
            )
            if propagated_single_p > 0:
                single_noncliff_channels[q] = (
                    0.15 * propagated_single_p,
                    0.35 * propagated_single_p,
                    0.50 * propagated_single_p,
                )

    local_pair_p = _clip_prob(0.45 * params["noncliff_p"] / max(1, max_pair_degree))
    local_hook_p = _clip_prob(0.35 * params["noncliff_p"] / max(1, max_pair_degree))

    events: List[EffectiveFaultEvent] = []
    for check in schedule.check_schedules:
        for site in check.noncliff_sites:
            q1, q2 = site.pair_qubits
            anchor = site.anchor_qubit

            if local_pair_p > 0:
                events.append(
                    _make_fault_event(
                        schedule=schedule,
                        source_check=check.check_index,
                        location_kind="nonclifford_interaction",
                        probability=0.50 * local_pair_p,
                        pauli_targets=(("Z", q1), ("Z", q2)),
                        explanation=(
                            "Propagated kickback on the dressed pair, reduced to an end-of-round ZZ event."
                        ),
                    )
                )
                events.append(
                    _make_fault_event(
                        schedule=schedule,
                        source_check=check.check_index,
                        location_kind="nonclifford_interaction",
                        probability=0.25 * local_pair_p,
                        pauli_targets=(("Y", q1), ("Z", q2)),
                        explanation=(
                            "A non-Clifford local Pauli fault can leave one partner with residual Y while kicking Z to the other."
                        ),
                    )
                )
                events.append(
                    _make_fault_event(
                        schedule=schedule,
                        source_check=check.check_index,
                        location_kind="nonclifford_interaction",
                        probability=0.25 * local_pair_p,
                        pauli_targets=(("Z", q1), ("Y", q2)),
                        explanation=(
                            "Mirror image of the propagated YZ event on the dressed pair."
                        ),
                    )
                )

            if local_hook_p > 0:
                events.append(
                    _make_fault_event(
                        schedule=schedule,
                        source_check=check.check_index,
                        location_kind="nonclifford_interaction",
                        probability=0.50 * local_hook_p,
                        pauli_targets=(("Z", anchor), ("Z", q1)),
                        explanation=(
                            "Ancilla-control fault approximated as a graphlike hook from the measured color to one dressed partner."
                        ),
                    )
                )
                events.append(
                    _make_fault_event(
                        schedule=schedule,
                        source_check=check.check_index,
                        location_kind="nonclifford_interaction",
                        probability=0.50 * local_hook_p,
                        pauli_targets=(("Z", anchor), ("Z", q2)),
                        explanation=(
                            "Second half of the graphlike hook approximation from the measured color to the other dressed partner."
                        ),
                    )
                )

    meas_flip_p = _combine_independent_probabilities(
        params["meas_p"],
        0.50 * params["init_p"],
        0.50 * params["oneq_p"],
        0.25 * params["twoq_p"],
    )
    final_readout_flip_p = _combine_independent_probabilities(
        params["meas_p"],
        0.50 * params["idle_p"],
    )

    return CircuitLevelNoiseSummary(
        prep_depolarize_p=prep_depolarize_p,
        round_depolarize_p=round_depolarize_p,
        tail_depolarize_p=tail_depolarize_p,
        single_noncliff_channels=single_noncliff_channels,
        correlated_events=tuple(events),
        meas_flip_p=meas_flip_p,
        final_readout_flip_p=final_readout_flip_p,
        model_label="circuit_level_effective_v1_graphlike_hooks",
    )


def _append_correlated_pauli_event(
    circuit: "stim.Circuit",
    event: EffectiveFaultEvent,
) -> None:
    if event.probability <= 0:
        return
    targets: List["stim.GateTarget"] = []
    for axis, qubit in event.pauli_targets:
        if axis == "X":
            targets.append(stim.target_x(qubit))
        elif axis == "Y":
            targets.append(stim.target_y(qubit))
        elif axis == "Z":
            targets.append(stim.target_z(qubit))
        else:
            raise ValueError(f"Unsupported Pauli axis: {axis}")
    circuit.append("CORRELATED_ERROR", targets, event.probability)


def _append_detector_layout(
    circuit: "stim.Circuit",
    *,
    round_index: int,
    n_checks: int,
) -> None:
    if round_index == 0:
        for check_index in range(n_checks):
            cur = stim.target_rec(-(n_checks - check_index))
            circuit.append("DETECTOR", [cur])
        return

    for check_index in range(n_checks):
        cur = stim.target_rec(-(n_checks - check_index))
        prev = stim.target_rec(-(2 * n_checks - check_index))
        circuit.append("DETECTOR", [cur, prev])


def _append_final_readout_layout(
    circuit: "stim.Circuit",
    *,
    x_stabs_qubits: Sequence[Sequence[int]],
    obs_paths: Sequence[Sequence[int]],
    n_data: int,
) -> None:
    n_checks = len(x_stabs_qubits)
    for check_index, qubits in enumerate(x_stabs_qubits):
        last_mpp = stim.target_rec(-(n_data + n_checks - check_index))
        recs = [stim.target_rec(-(n_data - q)) for q in qubits]
        circuit.append("DETECTOR", [last_mpp] + recs)

    for observable_index, path in enumerate(obs_paths):
        targets = [stim.target_rec(-(n_data - q)) for q in path]
        circuit.append("OBSERVABLE_INCLUDE", targets, observable_index)


def _phenomenological_kickback_probs(kick_p: float) -> Optional[List[float]]:
    kick_p = _clip_prob(kick_p)
    if kick_p <= 0:
        return None

    # A hidden ancilla-phase fault can dress either member of the CZ pair with Z,
    # or both members simultaneously, without introducing X/Y components.
    probs = [0.0] * 15
    probs[2] = kick_p * (1.0 - kick_p)   # IZ
    probs[11] = kick_p * (1.0 - kick_p)  # ZI
    probs[14] = kick_p * kick_p          # ZZ
    return probs


def _resolve_phenomenological_params(
    *,
    p: float,
    data_scale: Optional[float],
    meas_scale: Optional[float],
    kickback_scale: Optional[float],
) -> Dict[str, float]:
    data_p = _clip_prob(float(CFG["phenomenological_data_scale"] if data_scale is None else data_scale) * p)
    meas_p = _clip_prob(float(CFG["phenomenological_meas_scale"] if meas_scale is None else meas_scale) * p)
    kick_p = _clip_prob(float(CFG["phenomenological_kickback_scale"] if kickback_scale is None else kickback_scale) * p)
    return {"data_p": data_p, "meas_p": meas_p, "kick_p": kick_p}


def _append_phenomenological_kickback(
    circuit: "stim.Circuit",
    *,
    stab: D4Stabilizers,
    kick_p: float,
) -> None:
    probs = _phenomenological_kickback_probs(kick_p)
    if probs is None:
        return

    for v_stab in stab.vertex_X:
        color1, color2 = v_stab.cz_colors
        for edge1, edge2 in v_stab.cz_edge_pairs:
            q1 = edge_color_to_qubit(edge1, color1)
            q2 = edge_color_to_qubit(edge2, color2)
            circuit.append("PAULI_CHANNEL_2", [q1, q2], probs)


def build_phenomenological_x_circuit(
    *,
    stab: D4Stabilizers,
    rounds: int,
    p: float,
    data_scale: Optional[float] = None,
    meas_scale: Optional[float] = None,
    kickback_scale: Optional[float] = None,
    final_noise: bool = True,
) -> PhenomenologicalXArtifacts:
    """Phenomenological surrogate 回路。

    `data_scale`, `meas_scale`, `kickback_scale` を渡すと p に掛かる係数を
    変更でき、None の場合は CFG の `phenomenological_*_scale` を使う。
    `kickback_scale` は『2026-05-20_Tsimでphenomenologicalを正当化.py』で
    Tsim 厳密と比較して最適値を sweep するためのつまみ
    （depolarizing 版の `dressing_scale` と同じ役割）。
    """
    if stim is None:
        raise RuntimeError("stim is not available.")

    params = _resolve_phenomenological_params(
        p=p,
        data_scale=data_scale,
        meas_scale=meas_scale,
        kickback_scale=kickback_scale,
    )

    lat = stab.lat
    n_data = 3 * len(lat.edges)
    data = list(range(n_data))
    obs_paths = build_dual_x_observable_paths(lat)
    x_stabs_qubits = build_vertex_x_measurement_supports(stab)
    n_checks = len(x_stabs_qubits)
    data_p = params["data_p"]
    meas_p = params["meas_p"]
    kick_p = params["kick_p"]

    circuit = stim.Circuit()
    circuit.append("R", data)
    circuit.append("H", data)

    for round_index in range(rounds):
        if data_p > 0:
            circuit.append("DEPOLARIZE1", data, data_p)
        _append_phenomenological_kickback(
            circuit,
            stab=stab,
            kick_p=kick_p,
        )
        _append_mpp_round(circuit, x_stabs_qubits, meas_p=meas_p)
        _append_detector_layout(circuit, round_index=round_index, n_checks=n_checks)

    if final_noise and data_p > 0:  # v6: final_noise=False -> perfect final round
        circuit.append("DEPOLARIZE1", data, data_p)
    if final_noise and meas_p > 0:
        circuit.append("Z_ERROR", data, meas_p)
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
    return PhenomenologicalXArtifacts(
        circuit=circuit,
        dem=dem,
        n_observables=len(obs_paths),
        model_label="phenomenological_with_kickback",
    )