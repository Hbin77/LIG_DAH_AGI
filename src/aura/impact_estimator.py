from __future__ import annotations

from src.shared.metrics import clamp, compute_mvp_mission_impact
from src.shared.schemas import AttackCandidate, MissionState


KB_PER_MBIT = 125.0


def estimate_candidate_effect(
    state: MissionState,
    candidate: AttackCandidate,
    horizon_sec: float = 120.0,
) -> dict[str, float]:
    link = state.links.get(candidate.target_link) or state.links[state.active_link]
    base_capacity = max(link.bandwidth_mbps * KB_PER_MBIT, 1.0)
    capacity = base_capacity
    if candidate.bandwidth_limit_mbps is not None:
        capacity = min(capacity, max(candidate.bandwidth_limit_mbps * KB_PER_MBIT, 1.0))

    pressure_kb = 0.0
    if candidate.queue_pressure:
        pressure_kb += 1800.0
    if candidate.attack_type == "critical_window_degradation":
        pressure_kb += 600.0

    critical_queue_kb = (
        state.queue_kb_by_type.get("air_defense_alert", 0.0)
        + state.queue_kb_by_type.get("command", 0.0)
        + state.queue_kb_by_type.get("coordinate", 0.0)
    )
    video_queue_kb = state.video_queue_kb + pressure_kb
    total_queue_kb = state.total_queue_kb + pressure_kb

    fifo_queue_delay = total_queue_kb / capacity
    critical_pressure_delay = (critical_queue_kb + 0.35 * video_queue_kb) / capacity
    latency_delay = (link.base_latency_ms + candidate.latency_ms_add) / 1000.0
    jitter_delay = (link.jitter_ms + candidate.jitter_ms_add) / 1000.0
    loss_penalty = 20.0 * clamp(link.loss_rate + candidate.packet_loss_add, 0.0, 0.4)

    critical_window_bonus = 12.0 if candidate.attack_type == "critical_window_degradation" else 0.0
    phase_bonus = 10.0 if state.mission_phase == "air_defense_watch" else 0.0
    estimated_p95_latency = (
        state.recent_p95_critical_latency_sec
        + latency_delay
        + 0.5 * jitter_delay
        + critical_pressure_delay
        + 0.25 * fifo_queue_delay
        + loss_penalty
        + critical_window_bonus
        + phase_bonus
    )

    stale_add = 0.08 + candidate.latency_ms_add / 12000.0
    if candidate.bandwidth_limit_mbps is not None:
        stale_add += 0.08
    if candidate.attack_type == "stale_cop_induction":
        stale_add += 0.18
    estimated_stale_ratio = clamp(state.stale_data_ratio + stale_add)

    total_kb = max(total_queue_kb, 1.0)
    video_share = video_queue_kb / total_kb
    priority_inversion = clamp(
        state.priority_inversion_rate
        + 0.18 * video_share
        + (0.20 if candidate.queue_pressure else 0.0)
        + (0.08 if candidate.bandwidth_limit_mbps is not None else 0.0)
    )

    impact = compute_mvp_mission_impact(
        estimated_p95_latency,
        estimated_stale_ratio,
        priority_inversion,
    )
    return {
        "p95_critical_latency_sec": estimated_p95_latency,
        "stale_data_ratio": estimated_stale_ratio,
        "priority_inversion_rate": priority_inversion,
        "mission_impact": impact,
    }


def estimate_detectability(candidate: AttackCandidate, predicted: dict[str, float]) -> float:
    score = 0.0
    if candidate.packet_loss_add >= 0.10:
        score += 0.40
    elif candidate.packet_loss_add >= 0.05:
        score += 0.25
    if candidate.latency_ms_add >= 1200:
        score += 0.35
    elif candidate.latency_ms_add >= 700:
        score += 0.20
    if candidate.bandwidth_limit_mbps is not None and candidate.bandwidth_limit_mbps <= 0.7:
        score += 0.30
    elif candidate.bandwidth_limit_mbps is not None:
        score += 0.15
    if predicted.get("p95_critical_latency_sec", 0.0) > 75:
        score += 0.20
    return clamp(score)

