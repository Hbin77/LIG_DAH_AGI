from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


CRITICAL_TYPES = {"air_defense_alert", "command", "coordinate"}
MESSAGE_PRIORITIES = {
    "air_defense_alert": 10,
    "command": 9,
    "coordinate": 8,
    "telemetry": 5,
    "video": 2,
}
MESSAGE_DEADLINES_SEC = {
    "air_defense_alert": 3.0,
    "command": 5.0,
    "coordinate": 5.0,
    "telemetry": 15.0,
    "video": 30.0,
}
MESSAGE_SIZES_KB = {
    "air_defense_alert": 8.0,
    "command": 12.0,
    "coordinate": 10.0,
    "telemetry": 32.0,
    "video": 1200.0,
}


@dataclass
class Message:
    id: str
    type: str
    source: str
    destination: str
    created_at: float
    size_kb: float
    priority: int
    deadline_sec: float
    route: str
    remaining_kb: float | None = None
    delivered_at: float | None = None
    dropped: bool = False

    def __post_init__(self) -> None:
        if self.remaining_kb is None:
            self.remaining_kb = self.size_kb

    @property
    def is_critical(self) -> bool:
        return self.type in CRITICAL_TYPES


@dataclass
class LinkState:
    name: str
    available: bool
    bandwidth_mbps: float
    base_latency_ms: float
    jitter_ms: float
    loss_rate: float
    queue_depth: int = 0

    def copy(self) -> "LinkState":
        return LinkState(**asdict(self))


@dataclass
class AttackCandidate:
    attack_type: str
    target_link: str
    target_traffic_classes: list[str]
    start_time: float
    duration_sec: float
    latency_ms_add: float = 0.0
    jitter_ms_add: float = 0.0
    packet_loss_add: float = 0.0
    bandwidth_limit_mbps: float | None = None
    queue_pressure: bool = False
    reason: str = ""


@dataclass
class AttackEvent:
    event_id: str
    selected_at: float
    candidate: AttackCandidate
    expected_impact: dict[str, float]
    reason: str
    score: float
    agent: str = "AURA"


@dataclass
class DefenseEvent:
    event_id: str
    time_sec: float
    action: str
    details: dict[str, Any] = field(default_factory=dict)
    agent: str = "TSRA-R"


@dataclass
class MetricSnapshot:
    time_sec: float
    p95_critical_latency_sec: float
    stale_data_ratio: float
    trusted_stale_exposure: float
    priority_inversion_rate: float
    kill_chain_delay_sec: float
    recovery_instability: float
    mission_impact: float
    delivered_count: int
    dropped_count: int


@dataclass
class MissionState:
    time_sec: float
    mission_phase: str
    active_link: str
    links: dict[str, LinkState]
    queue_count_by_type: dict[str, int]
    queue_kb_by_type: dict[str, float]
    total_queue_kb: float
    critical_pending: int
    video_queue_kb: float
    stale_data_ratio: float
    recent_p95_critical_latency_sec: float
    priority_inversion_rate: float
    defense_mode: str = "none"


def to_plain_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {k: to_plain_dict(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: to_plain_dict(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_plain_dict(v) for v in value]
    return value
