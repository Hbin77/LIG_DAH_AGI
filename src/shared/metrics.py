from __future__ import annotations

from statistics import mean


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def normalize_metric_values(
    p95_critical_latency_sec: float,
    stale_data_ratio: float,
    priority_inversion_rate: float,
    kill_chain_delay_sec: float = 0.0,
    recovery_instability: float = 0.0,
) -> dict[str, float]:
    return {
        "critical_latency_score": clamp(p95_critical_latency_sec / 60.0),
        "stale_data_score": clamp(stale_data_ratio / 0.5),
        "priority_inversion_score": clamp(priority_inversion_rate / 0.4),
        "kill_chain_delay_score": clamp(kill_chain_delay_sec / 180.0),
        "recovery_instability_score": clamp(recovery_instability / 3.0),
    }


def compute_mvp_mission_impact(
    p95_critical_latency_sec: float,
    stale_data_ratio: float,
    priority_inversion_rate: float,
) -> float:
    scores = normalize_metric_values(
        p95_critical_latency_sec,
        stale_data_ratio,
        priority_inversion_rate,
    )
    return (
        0.50 * scores["critical_latency_score"]
        + 0.30 * scores["stale_data_score"]
        + 0.20 * scores["priority_inversion_score"]
    )


def compute_full_mission_impact(
    p95_critical_latency_sec: float,
    stale_data_ratio: float,
    priority_inversion_rate: float,
    kill_chain_delay_sec: float,
    recovery_instability: float,
) -> float:
    scores = normalize_metric_values(
        p95_critical_latency_sec,
        stale_data_ratio,
        priority_inversion_rate,
        kill_chain_delay_sec,
        recovery_instability,
    )
    return (
        0.35 * scores["critical_latency_score"]
        + 0.25 * scores["stale_data_score"]
        + 0.20 * scores["priority_inversion_score"]
        + 0.15 * scores["kill_chain_delay_score"]
        + 0.05 * scores["recovery_instability_score"]
    )


def compute_attack_score(mission_impact: float, detectability_score: float) -> float:
    return mission_impact - 0.15 * clamp(detectability_score)


def safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0

