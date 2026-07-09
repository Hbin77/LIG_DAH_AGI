from __future__ import annotations

from statistics import quantiles
from typing import Any

from .models import RunMetrics


def percentile_95(values: list[int]) -> float:
    if not values:
        return 0.0
    if len(values) < 20:
        return float(max(values))
    return float(quantiles(values, n=20, method="inclusive")[18])


def evaluate(events: list[dict[str, Any]], detection_tick: int | None, recovery_tick: int | None) -> RunMetrics:
    delivered = [event for event in events if event["event"] == "delivered"]
    lost = [event for event in events if event["event"] == "lost"]
    deferred = [event for event in events if event["event"] == "deferred"]
    shed = [event for event in events if event["event"] == "shed"]
    compressed = [event for event in events if event["event"] == "compressed"]
    backlog = [event for event in events if event["event"] == "backlog"]
    expired = [event for event in backlog if event.get("expired")]
    critical = [event for event in delivered if event["critical"]]
    critical_latencies = [int(event["latency"]) for event in critical]
    freshness_records = delivered + compressed
    stale = [event for event in freshness_records if event["stale"]]
    inversions = [event for event in delivered if event.get("priority_inversion")]
    generated_ids = {event["msg_id"] for event in events if "msg_id" in event}
    max_tick = max((int(event["tick"]) for event in events if "tick" in event), default=0)
    attack_ticks = [
        int(event["tick"])
        for event in events
        if event["event"] == "attack_action" and event.get("mode") != "none" and "tick" in event
    ]
    attack_start_tick = min(attack_ticks) if attack_ticks else None
    attack_end_tick = max(attack_ticks) if attack_ticks else None
    false_alarm_count = len(
        [
            event
            for event in events
            if event["event"] == "defense_action"
            and attack_start_tick is None
            and event.get("alert")
        ]
    )
    false_alarm_rate = false_alarm_count / (max_tick + 1) if max_tick >= 0 else 0.0
    detection_time = (
        max(0, detection_tick - attack_start_tick)
        if attack_start_tick is not None and detection_tick is not None
        else None
    )
    recovery_time = (
        max(0, recovery_tick - detection_tick)
        if detection_tick is not None and recovery_tick is not None
        else None
    )

    delivered_count = len(delivered)
    freshness_count = len(freshness_records)
    stale_ratio = len(stale) / freshness_count if freshness_count else 0.0
    critical_count = len(critical)
    inversion_rate = len(inversions) / critical_count if critical_count else 0.0
    p95 = percentile_95(critical_latencies)

    impact = (
        p95 * 1.8
        + stale_ratio * 45.0
        + inversion_rate * 35.0
        + len(lost) * 0.35
        + len(deferred) * 0.08
        + len(shed) * 0.04
        + len(compressed) * 0.035
        + len(backlog) * 0.12
        + len(expired) * 0.30
        + false_alarm_count * 0.15
    )
    if attack_start_tick is not None and detection_tick is None:
        impact += 12.0
    if attack_start_tick is not None and recovery_tick is None:
        impact += 8.0

    return RunMetrics(
        generated_messages=len(generated_ids),
        delivered_messages=delivered_count,
        lost_messages=len(lost),
        deferred_messages=len(deferred),
        shed_messages=len(shed),
        compressed_messages=len(compressed),
        backlog_messages=len(backlog),
        expired_messages=len(expired),
        p95_critical_latency=round(p95, 2),
        stale_data_ratio=round(stale_ratio, 4),
        priority_inversion_rate=round(inversion_rate, 4),
        false_alarm_count=false_alarm_count,
        false_alarm_rate=round(false_alarm_rate, 4),
        attack_start_tick=attack_start_tick,
        attack_end_tick=attack_end_tick,
        detection_tick=detection_tick,
        recovery_tick=recovery_tick,
        detection_time=detection_time,
        recovery_time=recovery_time,
        mission_impact_score=round(impact, 2),
    )


def resilience_gain(attacked: RunMetrics, defended: RunMetrics, baseline: RunMetrics | None = None) -> float:
    baseline_score = baseline.mission_impact_score if baseline else 0.0
    denominator = attacked.mission_impact_score - baseline_score
    if denominator <= 0:
        return 0.0
    gain = (attacked.mission_impact_score - defended.mission_impact_score) / denominator
    return round(gain * 100.0, 2)
