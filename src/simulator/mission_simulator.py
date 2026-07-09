from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.shared.event_log import JsonlLogger
from src.shared.metrics import compute_full_mission_impact, percentile
from src.shared.schemas import (
    CRITICAL_TYPES,
    MESSAGE_DEADLINES_SEC,
    MESSAGE_PRIORITIES,
    MESSAGE_SIZES_KB,
    AttackCandidate,
    AttackEvent,
    DefenseEvent,
    LinkState,
    Message,
    MetricSnapshot,
    MissionState,
)


KB_PER_MBIT = 125.0


def default_links() -> dict[str, LinkState]:
    return {
        "SATCOM": LinkState("SATCOM", True, 5.0, 650.0, 80.0, 0.01),
        "TACTICAL_RADIO": LinkState("TACTICAL_RADIO", True, 0.8, 260.0, 50.0, 0.02),
        "LTE": LinkState("LTE", True, 3.0, 120.0, 35.0, 0.015),
        "MESH": LinkState("MESH", True, 1.2, 180.0, 45.0, 0.018),
    }


class MissionSimulator:
    def __init__(
        self,
        duration_sec: int = 300,
        seed: int = 7,
        output_dir: Path | str = Path("outputs/run"),
    ) -> None:
        self.duration_sec = duration_sec
        self.rng = random.Random(seed)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.base_links = default_links()
        self.queues: dict[str, list[Message]] = {name: [] for name in self.base_links}
        self.in_flight: list[tuple[float, Message]] = []
        self.delivered_messages: list[Message] = []
        self.dropped_messages: list[Message] = []
        self.attack_events: list[AttackEvent] = []
        self.defense_events: list[DefenseEvent] = []
        self.metric_snapshots: list[MetricSnapshot] = []
        self.active_link = "SATCOM"
        self.defense_mode = "none"
        self.priority_routing_until = 0.0
        self.video_throttle_until = 0.0
        self.stale_badge_until = 0.0
        self.pace_switch_count = 0
        self.priority_inversion_count = 0
        self.transmitted_count = 0
        self.msg_counter = 0
        self.time_sec = 0.0
        self.cop_objects = {
            "UAV-01": {"last_update": 0.0, "limit": 30.0},
            "UGV-02": {"last_update": 0.0, "limit": 20.0},
            "POST-ALPHA": {"last_update": 0.0, "limit": 15.0},
            "AIR-THREAT": {"last_update": 0.0, "limit": 10.0},
        }

        self.mission_log = JsonlLogger(self.output_dir / "mission_events.jsonl")
        self.attack_log = JsonlLogger(self.output_dir / "attack_events.jsonl")
        self.defense_log = JsonlLogger(self.output_dir / "defense_events.jsonl")
        self.metric_log = JsonlLogger(self.output_dir / "metric_snapshots.jsonl")

    def run(
        self,
        aura: Any | None = None,
        defender: Any | None = None,
        fixed_attacks: list[AttackEvent] | None = None,
    ) -> dict[str, float]:
        if fixed_attacks:
            for event in fixed_attacks:
                self._register_attack(event)

        for tick in range(self.duration_sec + 1):
            self.time_sec = float(tick)
            self._generate_attack_pressure()
            self._generate_messages()

            if aura and tick % 10 == 0:
                event = aura.decide(self.snapshot_state())
                if event:
                    self._register_attack(event)

            if defender and tick % 5 == 0:
                for event in defender.decide(self.snapshot_state()):
                    self._apply_defense(event)

            self._process_queues()
            self._deliver_in_flight()

            if tick % 5 == 0:
                snapshot = self._metric_snapshot()
                self.metric_snapshots.append(snapshot)
                self.metric_log.write(snapshot)

        summary = self.summary()
        self._write_summary_csv(summary)
        return summary

    def snapshot_state(self) -> MissionState:
        effective_links = {
            name: self._effective_link_state(name, self.time_sec) for name in self.base_links
        }
        queue_count_by_type: dict[str, int] = defaultdict(int)
        queue_kb_by_type: dict[str, float] = defaultdict(float)
        total_queue_kb = 0.0
        critical_pending = 0
        for queue in self.queues.values():
            for msg in queue:
                queue_count_by_type[msg.type] += 1
                queue_kb_by_type[msg.type] += msg.remaining_kb or 0.0
                total_queue_kb += msg.remaining_kb or 0.0
                if msg.is_critical:
                    critical_pending += 1
        for name, link in effective_links.items():
            link.queue_depth = len(self.queues[name])
        return MissionState(
            time_sec=self.time_sec,
            mission_phase=self._mission_phase(self.time_sec),
            active_link=self.active_link,
            links=effective_links,
            queue_count_by_type=dict(queue_count_by_type),
            queue_kb_by_type=dict(queue_kb_by_type),
            total_queue_kb=total_queue_kb,
            critical_pending=critical_pending,
            video_queue_kb=queue_kb_by_type.get("video", 0.0),
            stale_data_ratio=self._stale_data_ratio(self.time_sec),
            recent_p95_critical_latency_sec=self._p95_critical_latency(),
            priority_inversion_rate=self._priority_inversion_rate(),
            defense_mode=self.defense_mode,
        )

    def summary(self) -> dict[str, float]:
        final = self.metric_snapshots[-1] if self.metric_snapshots else self._metric_snapshot()
        critical_delivered = [
            msg
            for msg in self.delivered_messages
            if msg.type in CRITICAL_TYPES and msg.delivered_at is not None
        ]
        return {
            "p95_critical_latency_sec": final.p95_critical_latency_sec,
            "stale_data_ratio": final.stale_data_ratio,
            "trusted_stale_exposure": final.trusted_stale_exposure,
            "priority_inversion_rate": final.priority_inversion_rate,
            "kill_chain_delay_sec": final.kill_chain_delay_sec,
            "recovery_instability": final.recovery_instability,
            "mission_impact": final.mission_impact,
            "delivered_count": float(len(self.delivered_messages)),
            "dropped_count": float(len(self.dropped_messages)),
            "critical_delivered_count": float(len(critical_delivered)),
            "attack_count": float(len(self.attack_events)),
            "defense_count": float(len(self.defense_events)),
        }

    def _register_attack(self, event: AttackEvent) -> None:
        self.attack_events.append(event)
        self.attack_log.write(event)

    def _apply_defense(self, event: DefenseEvent) -> None:
        self.defense_events.append(event)
        self.defense_log.write(event)
        action = event.action
        details = event.details
        until = float(details.get("until_sec", self.time_sec + 60))
        if action == "priority_reroute":
            self.priority_routing_until = max(self.priority_routing_until, until)
            self.defense_mode = "tsra_r"
        elif action == "video_throttle":
            self.video_throttle_until = max(self.video_throttle_until, until)
            self.defense_mode = "tsra_r"
        elif action == "stale_badge":
            self.stale_badge_until = max(self.stale_badge_until, until)
            self.defense_mode = "tsra_r"
        elif action == "pace_switch":
            target = details.get("target_link")
            if target in self.queues:
                old = self.active_link
                self.active_link = target
                self.defense_mode = "pace_switch"
                self.pace_switch_count += 1
                if details.get("move_critical"):
                    self._move_critical_messages(old, target)

    def _move_critical_messages(self, source_link: str, target_link: str) -> None:
        kept = []
        moved = []
        for msg in self.queues[source_link]:
            if msg.is_critical:
                msg.route = target_link
                moved.append(msg)
            else:
                kept.append(msg)
        self.queues[source_link] = kept
        self.queues[target_link].extend(moved)

    def _generate_messages(self) -> None:
        phase = self._mission_phase(self.time_sec)
        self._maybe_create("telemetry", "UGV-02", 0.72)
        self._maybe_create("coordinate", "UAV-01", 0.12)
        self._maybe_create("video", "UAV-01", 0.13 if phase != "air_defense_watch" else 0.20)
        self._maybe_create("command", "HQ", 0.03)
        if phase == "air_defense_watch":
            self._maybe_create("air_defense_alert", "POST-ALPHA", 0.22)
        elif phase == "resupply_move":
            self._maybe_create("coordinate", "UGV-02", 0.18)

    def _maybe_create(self, msg_type: str, source: str, probability: float) -> None:
        if self.rng.random() > probability:
            return
        self.msg_counter += 1
        size = MESSAGE_SIZES_KB[msg_type] * self.rng.uniform(0.85, 1.15)
        msg = Message(
            id=f"msg-{self.msg_counter:06d}",
            type=msg_type,
            source=source,
            destination="HQ",
            created_at=self.time_sec,
            size_kb=size,
            priority=MESSAGE_PRIORITIES[msg_type],
            deadline_sec=MESSAGE_DEADLINES_SEC[msg_type],
            route=self.active_link,
        )
        if msg_type == "video" and self.time_sec < self.video_throttle_until:
            msg.size_kb *= 0.25
            msg.remaining_kb = msg.size_kb
        self.queues[msg.route].append(msg)
        self.mission_log.write({"time_sec": self.time_sec, "event": "message_created", "message": msg})

    def _generate_attack_pressure(self) -> None:
        for event in self._active_attacks(self.time_sec):
            candidate = event.candidate
            if not candidate.queue_pressure:
                continue
            if int(self.time_sec) % 4 != 0:
                continue
            self.msg_counter += 1
            msg = Message(
                id=f"atk-video-{self.msg_counter:06d}",
                type="video",
                source="UAV-01",
                destination="HQ",
                created_at=self.time_sec,
                size_kb=1500.0,
                priority=MESSAGE_PRIORITIES["video"],
                deadline_sec=MESSAGE_DEADLINES_SEC["video"],
                route=candidate.target_link,
            )
            self.queues[candidate.target_link].append(msg)
            self.mission_log.write(
                {"time_sec": self.time_sec, "event": "attack_queue_pressure", "message": msg}
            )

    def _process_queues(self) -> None:
        for link_name in list(self.queues):
            link = self._effective_link_state(link_name, self.time_sec)
            if not link.available:
                continue
            capacity_kb = max(link.bandwidth_mbps * KB_PER_MBIT, 1.0)
            spent_guard = 0
            while capacity_kb > 0 and self.queues[link_name] and spent_guard < 500:
                spent_guard += 1
                idx = self._select_queue_index(link_name)
                if idx is None:
                    break
                queue = self.queues[link_name]
                msg = queue[idx]
                max_waiting_priority = max((m.priority for m in queue), default=msg.priority)
                if msg.priority < max_waiting_priority:
                    self.priority_inversion_count += 1
                self.transmitted_count += 1
                chunk = min(capacity_kb, msg.remaining_kb or 0.0)
                msg.remaining_kb = (msg.remaining_kb or 0.0) - chunk
                capacity_kb -= chunk
                if msg.remaining_kb <= 0:
                    queue.pop(idx)
                    self._schedule_delivery(msg, link)
                else:
                    break

    def _select_queue_index(self, link_name: str) -> int | None:
        queue = self.queues[link_name]
        if not queue:
            return None
        critical_waiting = any(msg.is_critical for msg in queue)
        if self.time_sec < self.priority_routing_until:
            candidates = list(enumerate(queue))
            if self.time_sec < self.video_throttle_until and critical_waiting:
                non_video = [(i, msg) for i, msg in candidates if msg.type != "video"]
                if non_video:
                    candidates = non_video
            return max(candidates, key=lambda item: (item[1].priority, -item[1].created_at))[0]
        if self.time_sec < self.video_throttle_until and critical_waiting:
            for i, msg in enumerate(queue):
                if msg.type != "video":
                    return i
        return 0

    def _schedule_delivery(self, msg: Message, link: LinkState) -> None:
        loss = min(max(link.loss_rate, 0.0), 0.95)
        if self.rng.random() < loss:
            msg.dropped = True
            self.dropped_messages.append(msg)
            self.mission_log.write({"time_sec": self.time_sec, "event": "message_dropped", "message": msg})
            return
        jitter = abs(self.rng.gauss(0.0, link.jitter_ms / 1000.0))
        deliver_at = self.time_sec + max(link.base_latency_ms / 1000.0 + jitter, 0.0)
        self.in_flight.append((deliver_at, msg))

    def _deliver_in_flight(self) -> None:
        remaining: list[tuple[float, Message]] = []
        for deliver_at, msg in self.in_flight:
            if deliver_at <= self.time_sec:
                msg.delivered_at = self.time_sec
                self.delivered_messages.append(msg)
                self._update_cop(msg)
                self.mission_log.write(
                    {"time_sec": self.time_sec, "event": "message_delivered", "message": msg}
                )
            else:
                remaining.append((deliver_at, msg))
        self.in_flight = remaining

    def _update_cop(self, msg: Message) -> None:
        if msg.type in {"telemetry", "coordinate"} and msg.source in self.cop_objects:
            self.cop_objects[msg.source]["last_update"] = self.time_sec
        if msg.type == "air_defense_alert":
            self.cop_objects["AIR-THREAT"]["last_update"] = self.time_sec

    def _effective_link_state(self, link_name: str, time_sec: float) -> LinkState:
        link = self.base_links[link_name].copy()
        for event in self._active_attacks(time_sec):
            c = event.candidate
            if c.target_link != link_name:
                continue
            link.base_latency_ms += c.latency_ms_add
            link.jitter_ms += c.jitter_ms_add
            link.loss_rate = min(link.loss_rate + c.packet_loss_add, 0.95)
            if c.bandwidth_limit_mbps is not None:
                link.bandwidth_mbps = min(link.bandwidth_mbps, c.bandwidth_limit_mbps)
        return link

    def _active_attacks(self, time_sec: float) -> list[AttackEvent]:
        return [
            event
            for event in self.attack_events
            if event.candidate.start_time <= time_sec < event.candidate.start_time + event.candidate.duration_sec
        ]

    def _metric_snapshot(self) -> MetricSnapshot:
        p95 = self._p95_critical_latency()
        stale = self._stale_data_ratio(self.time_sec)
        trusted_stale_exposure = self._trusted_stale_exposure(stale)
        inversion = self._priority_inversion_rate()
        kill_chain_delay = p95 + 60.0 * trusted_stale_exposure
        recovery = float(self.pace_switch_count)
        impact = compute_full_mission_impact(
            p95,
            trusted_stale_exposure,
            inversion,
            kill_chain_delay,
            recovery,
        )
        return MetricSnapshot(
            time_sec=self.time_sec,
            p95_critical_latency_sec=p95,
            stale_data_ratio=stale,
            trusted_stale_exposure=trusted_stale_exposure,
            priority_inversion_rate=inversion,
            kill_chain_delay_sec=kill_chain_delay,
            recovery_instability=recovery,
            mission_impact=impact,
            delivered_count=len(self.delivered_messages),
            dropped_count=len(self.dropped_messages),
        )

    def _p95_critical_latency(self) -> float:
        latencies = [
            (msg.delivered_at or self.time_sec) - msg.created_at
            for msg in self.delivered_messages
            if msg.type in CRITICAL_TYPES and msg.delivered_at is not None
        ]
        return percentile(latencies, 0.95)

    def _priority_inversion_rate(self) -> float:
        if self.transmitted_count == 0:
            return 0.0
        return min(self.priority_inversion_count / self.transmitted_count, 1.0)

    def _stale_data_ratio(self, time_sec: float) -> float:
        stale_count = 0
        for obj in self.cop_objects.values():
            if time_sec - obj["last_update"] > obj["limit"]:
                stale_count += 1
        return stale_count / max(len(self.cop_objects), 1)

    def _trusted_stale_exposure(self, stale_ratio: float) -> float:
        if self.time_sec < self.stale_badge_until:
            return stale_ratio * 0.25
        return stale_ratio

    @staticmethod
    def _mission_phase(time_sec: float) -> str:
        if 85 <= time_sec <= 145 or 215 <= time_sec <= 255:
            return "air_defense_watch"
        if 155 <= time_sec <= 205:
            return "resupply_move"
        return "normal_patrol"

    def _write_summary_csv(self, summary: dict[str, float]) -> None:
        path = self.output_dir / "summary.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
            writer.writeheader()
            writer.writerow(summary)


def fixed_attack_event(
    start_time: float = 95.0,
    attack_type: str = "link_degradation",
    target_link: str = "SATCOM",
) -> AttackEvent:
    candidate = AttackCandidate(
        attack_type=attack_type,
        target_link=target_link,
        target_traffic_classes=["all"],
        start_time=start_time,
        duration_sec=90.0,
        latency_ms_add=900.0,
        jitter_ms_add=180.0,
        packet_loss_add=0.04,
        bandwidth_limit_mbps=1.4,
        queue_pressure=attack_type == "queue_pressure",
        reason="fixed baseline attack for E2",
    )
    return AttackEvent(
        event_id="fixed-atk-00001",
        selected_at=start_time,
        candidate=candidate,
        expected_impact={},
        reason=candidate.reason,
        score=0.0,
        agent="fixed",
    )
