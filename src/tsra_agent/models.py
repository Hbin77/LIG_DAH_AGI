from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LinkName(str, Enum):
    SATCOM = "satcom"
    RADIO = "radio"
    LTE = "lte"
    MESH = "mesh"


class MessageType(str, Enum):
    UAV_VIDEO = "uav_video"
    UGV_STATUS = "ugv_status"
    SENSOR_ALERT = "sensor_alert"
    COMMAND = "command"
    POSITION = "position"


class AttackMode(str, Enum):
    NONE = "none"
    LINK_DEGRADATION = "link_degradation"
    MISSION_AWARE_DELAY = "mission_aware_delay"
    FAILOVER_CHASING = "failover_chasing"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class MessageProfile:
    msg_type: MessageType
    interval: int
    size_kb: int
    base_priority: int
    stale_after: int
    critical: bool


@dataclass
class LinkState:
    name: LinkName
    capacity_kb_per_tick: int
    base_latency: int
    loss_rate: float
    jitter: int
    health: float = 1.0

    def effective_capacity(self) -> int:
        return max(1, int(self.capacity_kb_per_tick * self.health))


@dataclass
class MissionMessage:
    msg_id: int
    msg_type: MessageType
    source: str
    created_tick: int
    size_kb: int
    base_priority: int
    stale_after: int
    critical: bool
    priority: int = field(init=False)

    def __post_init__(self) -> None:
        self.priority = self.base_priority


@dataclass
class AttackAction:
    mode: AttackMode
    target_link: LinkName
    intensity: float
    duration: int
    rationale: str


@dataclass
class DefenseAction:
    active_link: LinkName
    priority_boost: bool
    minimum_mode: bool
    alert: str | None
    stale_badge: bool
    risk_score: float = 0.0
    quarantine: bool = False
    pace_transition: bool = False


@dataclass
class RunMetrics:
    generated_messages: int
    delivered_messages: int
    lost_messages: int
    deferred_messages: int
    shed_messages: int
    compressed_messages: int
    backlog_messages: int
    expired_messages: int
    p95_critical_latency: float
    stale_data_ratio: float
    priority_inversion_rate: float
    false_alarm_count: int
    false_alarm_rate: float
    attack_start_tick: int | None
    attack_end_tick: int | None
    detection_tick: int | None
    recovery_tick: int | None
    detection_time: int | None
    recovery_time: int | None
    mission_impact_score: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "generated_messages": self.generated_messages,
            "delivered_messages": self.delivered_messages,
            "lost_messages": self.lost_messages,
            "deferred_messages": self.deferred_messages,
            "shed_messages": self.shed_messages,
            "compressed_messages": self.compressed_messages,
            "backlog_messages": self.backlog_messages,
            "expired_messages": self.expired_messages,
            "p95_critical_latency": self.p95_critical_latency,
            "stale_data_ratio": self.stale_data_ratio,
            "priority_inversion_rate": self.priority_inversion_rate,
            "false_alarm_count": self.false_alarm_count,
            "false_alarm_rate": self.false_alarm_rate,
            "attack_start_tick": self.attack_start_tick,
            "attack_end_tick": self.attack_end_tick,
            "detection_tick": self.detection_tick,
            "recovery_tick": self.recovery_tick,
            "detection_time": self.detection_time,
            "recovery_time": self.recovery_time,
            "mission_impact_score": self.mission_impact_score,
        }
