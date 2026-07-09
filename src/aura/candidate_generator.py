from __future__ import annotations

from src.shared.schemas import AttackCandidate, MissionState


def generate_candidates(state: MissionState) -> list[AttackCandidate]:
    start = state.time_sec
    target = state.active_link or "SATCOM"
    candidates = [
        AttackCandidate(
            attack_type="link_degradation",
            target_link=target,
            target_traffic_classes=["all"],
            start_time=start,
            duration_sec=60,
            latency_ms_add=700,
            jitter_ms_add=180,
            packet_loss_add=0.03,
            reason="general link quality degradation",
        ),
        AttackCandidate(
            attack_type="bandwidth_limit",
            target_link=target,
            target_traffic_classes=["all"],
            start_time=start,
            duration_sec=80,
            jitter_ms_add=80,
            packet_loss_add=0.02,
            bandwidth_limit_mbps=1.0,
            reason="reduce available capacity during queue growth",
        ),
        AttackCandidate(
            attack_type="queue_pressure",
            target_link=target,
            target_traffic_classes=["video", "telemetry"],
            start_time=start,
            duration_sec=80,
            latency_ms_add=200,
            jitter_ms_add=100,
            bandwidth_limit_mbps=1.5,
            queue_pressure=True,
            reason="increase non-critical queue occupancy",
        ),
    ]
    if state.mission_phase == "air_defense_watch" or state.critical_pending > 0:
        candidates.append(
            AttackCandidate(
                attack_type="critical_window_degradation",
                target_link=target,
                target_traffic_classes=["air_defense_alert", "command", "coordinate"],
                start_time=start,
                duration_sec=70,
                latency_ms_add=1200,
                jitter_ms_add=250,
                packet_loss_add=0.05,
                bandwidth_limit_mbps=1.2,
                reason="critical traffic is entering a high-consequence window",
            )
        )
    if state.stale_data_ratio > 0.2:
        candidates.append(
            AttackCandidate(
                attack_type="stale_cop_induction",
                target_link=target,
                target_traffic_classes=["telemetry", "coordinate"],
                start_time=start,
                duration_sec=70,
                latency_ms_add=800,
                jitter_ms_add=160,
                packet_loss_add=0.04,
                bandwidth_limit_mbps=1.0,
                reason="COP freshness is already degraded",
            )
        )
    if state.defense_mode in {"pace_switch", "tsra_r"} and state.active_link != "SATCOM":
        candidates.append(
            AttackCandidate(
                attack_type="failover_chasing",
                target_link=state.active_link,
                target_traffic_classes=["all"],
                start_time=start,
                duration_sec=70,
                latency_ms_add=600,
                jitter_ms_add=120,
                packet_loss_add=0.03,
                bandwidth_limit_mbps=0.45,
                reason="defender has shifted traffic to a constrained fallback link",
            )
        )
    return candidates

