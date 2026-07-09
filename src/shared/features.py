from __future__ import annotations

from src.shared.schemas import AttackCandidate, MissionState


MISSION_PHASES = ["normal_patrol", "air_defense_watch", "resupply_move"]
ATTACK_TYPES = [
    "link_degradation",
    "bandwidth_limit",
    "queue_pressure",
    "critical_window_degradation",
    "stale_cop_induction",
    "failover_chasing",
]
LINK_NAMES = ["SATCOM", "TACTICAL_RADIO", "LTE", "MESH"]


def candidate_features(state: MissionState, candidate: AttackCandidate) -> dict[str, float]:
    features: dict[str, float] = {
        "time_sec": state.time_sec,
        "total_queue_kb": state.total_queue_kb,
        "critical_pending": float(state.critical_pending),
        "video_queue_kb": state.video_queue_kb,
        "stale_data_ratio": state.stale_data_ratio,
        "recent_p95_critical_latency_sec": state.recent_p95_critical_latency_sec,
        "priority_inversion_rate": state.priority_inversion_rate,
        "latency_ms_add": candidate.latency_ms_add,
        "jitter_ms_add": candidate.jitter_ms_add,
        "packet_loss_add": candidate.packet_loss_add,
        "duration_sec": candidate.duration_sec,
        "bandwidth_limit_mbps": candidate.bandwidth_limit_mbps or 0.0,
        "queue_pressure": 1.0 if candidate.queue_pressure else 0.0,
    }
    active = state.links.get(state.active_link)
    if active:
        features.update(
            {
                "active_bandwidth_mbps": active.bandwidth_mbps,
                "active_latency_ms": active.base_latency_ms,
                "active_jitter_ms": active.jitter_ms,
                "active_loss_rate": active.loss_rate,
                "active_queue_depth": float(active.queue_depth),
            }
        )
    for phase in MISSION_PHASES:
        features[f"phase_{phase}"] = 1.0 if state.mission_phase == phase else 0.0
    for attack_type in ATTACK_TYPES:
        features[f"attack_{attack_type}"] = 1.0 if candidate.attack_type == attack_type else 0.0
    for link in LINK_NAMES:
        features[f"target_{link}"] = 1.0 if candidate.target_link == link else 0.0
        link_state = state.links.get(link)
        if link_state:
            features[f"{link}_bandwidth_mbps"] = link_state.bandwidth_mbps
            features[f"{link}_latency_ms"] = link_state.base_latency_ms
            features[f"{link}_loss_rate"] = link_state.loss_rate
            features[f"{link}_queue_depth"] = float(link_state.queue_depth)
    for message_type, count in state.queue_count_by_type.items():
        features[f"queue_count_{message_type}"] = float(count)
    for message_type, kb in state.queue_kb_by_type.items():
        features[f"queue_kb_{message_type}"] = float(kb)
    return features


def state_features(state: MissionState) -> dict[str, float]:
    features: dict[str, float] = {
        "time_sec": state.time_sec,
        "total_queue_kb": state.total_queue_kb,
        "critical_pending": float(state.critical_pending),
        "video_queue_kb": state.video_queue_kb,
        "stale_data_ratio": state.stale_data_ratio,
        "recent_p95_critical_latency_sec": state.recent_p95_critical_latency_sec,
        "priority_inversion_rate": state.priority_inversion_rate,
    }
    for phase in MISSION_PHASES:
        features[f"phase_{phase}"] = 1.0 if state.mission_phase == phase else 0.0
    for link in LINK_NAMES:
        features[f"active_{link}"] = 1.0 if state.active_link == link else 0.0
        link_state = state.links.get(link)
        if link_state:
            features[f"{link}_bandwidth_mbps"] = link_state.bandwidth_mbps
            features[f"{link}_latency_ms"] = link_state.base_latency_ms
            features[f"{link}_jitter_ms"] = link_state.jitter_ms
            features[f"{link}_loss_rate"] = link_state.loss_rate
            features[f"{link}_queue_depth"] = float(link_state.queue_depth)
    for message_type, count in state.queue_count_by_type.items():
        features[f"queue_count_{message_type}"] = float(count)
    for message_type, kb in state.queue_kb_by_type.items():
        features[f"queue_kb_{message_type}"] = float(kb)
    return features
