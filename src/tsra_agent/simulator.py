from __future__ import annotations

import json
import random
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .agents import AURALite, MissionState, MLTSRARLite, TSRARLite
from .evaluator import evaluate
from .models import (
    AttackMode,
    DefenseAction,
    LinkName,
    LinkState,
    MessageProfile,
    MessageType,
    MissionMessage,
    RunMetrics,
)
from .runtime import AgentTraceRecorder


DEFAULT_PROFILES = [
    MessageProfile(MessageType.UAV_VIDEO, interval=2, size_kb=850, base_priority=1, stale_after=8, critical=False),
    MessageProfile(MessageType.UGV_STATUS, interval=4, size_kb=90, base_priority=4, stale_after=10, critical=False),
    MessageProfile(MessageType.SENSOR_ALERT, interval=9, size_kb=25, base_priority=9, stale_after=5, critical=True),
    MessageProfile(MessageType.COMMAND, interval=11, size_kb=20, base_priority=10, stale_after=6, critical=True),
    MessageProfile(MessageType.POSITION, interval=5, size_kb=35, base_priority=8, stale_after=7, critical=True),
]


@dataclass
class SimulationResult:
    name: str
    events: list[dict[str, Any]]
    metrics: RunMetrics
    traces: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


@dataclass
class MissionSimulator:
    ticks: int
    seed: int
    attack_mode: AttackMode
    defense_enabled: bool
    defense_mode: str = "tsra"
    defense_config: dict[str, float] | None = None
    sklearn_model: object | None = None
    rng: random.Random = field(init=False)
    queue: deque[MissionMessage] = field(default_factory=deque)
    msg_counter: int = 0
    active_link: LinkName = LinkName.SATCOM
    events: list[dict[str, Any]] = field(default_factory=list)
    critical_latencies_window: deque[int] = field(default_factory=lambda: deque(maxlen=20))
    stale_window: deque[bool] = field(default_factory=lambda: deque(maxlen=30))
    inversion_window: deque[bool] = field(default_factory=lambda: deque(maxlen=30))
    terminal_risk_window: deque[float] = field(default_factory=lambda: deque(maxlen=20))
    source_trust_drop_window: deque[float] = field(default_factory=lambda: deque(maxlen=20))
    pace_instability_window: deque[float] = field(default_factory=lambda: deque(maxlen=20))
    max_noncritical_created_delivered: int = -1

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.links = {
            LinkName.SATCOM: LinkState(LinkName.SATCOM, 1100, 2, 0.02, 2),
            LinkName.RADIO: LinkState(LinkName.RADIO, 180, 3, 0.03, 1),
            LinkName.LTE: LinkState(LinkName.LTE, 420, 2, 0.05, 2),
            LinkName.MESH: LinkState(LinkName.MESH, 260, 4, 0.04, 2),
        }
        self.red = AURALite(self.attack_mode)
        if self.defense_mode == "ml":
            ml_kwargs: dict[str, Any] = {}
            if self.defense_config is not None:
                ml_kwargs["policy_config"] = self.defense_config
            if self.sklearn_model is not None:
                ml_kwargs["sklearn_model"] = self.sklearn_model
            self.blue = MLTSRARLite(**ml_kwargs)
        else:
            self.blue = TSRARLite()
        self.aura_trace = AgentTraceRecorder(
            "AURA-lite",
            "select bounded simulated mission-effect attacks",
        )
        blue_name = "TSRA-ML" if self.defense_mode == "ml" else "TSRA-R-lite"
        self.blue_trace = AgentTraceRecorder(
            blue_name,
            "detect and mitigate synthetic C4ISR data-trust degradation",
        )

    def run(self, name: str) -> SimulationResult:
        for tick in range(self.ticks):
            self._generate_messages(tick)
            state = self._state(tick)
            attack = self.red.choose_action(state)
            self._record_attack_decision(tick, state, attack)
            self._apply_attack(tick, attack)

            defense = DefenseAction(self.active_link, False, False, None, False)
            if self.defense_enabled:
                if self.defense_mode == "rule":
                    defense = self._rule_defense_action(tick, self._state(tick))
                else:
                    defense = self.blue.choose_action(self._state(tick))
                self._record_defense_decision(tick, self._state(tick), defense)
                self.active_link = defense.active_link
                self._apply_defense(tick, defense)
                if defense.minimum_mode:
                    self._shed_expired_noncritical(tick)
            else:
                self.pace_instability_window.append(0.0)

            self._process_queue(tick, attack.mode, defense)
            self._recover_links()

        self._flush_backlog(self.ticks)
        metrics = evaluate(self.events, self.blue.alert_tick, self.blue.recovery_tick)
        return SimulationResult(
            name=name,
            events=self.events,
            metrics=metrics,
            traces={
                "aura": self.aura_trace.traces,
                "tsra": self.blue_trace.traces,
            },
        )

    def _generate_messages(self, tick: int) -> None:
        for profile in DEFAULT_PROFILES:
            if tick % profile.interval == 0:
                self.msg_counter += 1
                self.queue.append(
                    MissionMessage(
                        msg_id=self.msg_counter,
                        msg_type=profile.msg_type,
                        source=self._source(profile.msg_type),
                        created_tick=tick,
                        size_kb=profile.size_kb,
                        base_priority=profile.base_priority,
                        stale_after=profile.stale_after,
                        critical=profile.critical,
                    )
                )

    def _source(self, msg_type: MessageType) -> str:
        return {
            MessageType.UAV_VIDEO: "UAV-1",
            MessageType.UGV_STATUS: "UGV-A",
            MessageType.SENSOR_ALERT: "OP-ALPHA",
            MessageType.COMMAND: "CP-MAIN",
            MessageType.POSITION: "BLUE-FORCE",
        }[msg_type]

    def _state(self, tick: int) -> MissionState:
        critical_depth = sum(1 for item in self.queue if item.critical)
        stale_ratio = sum(self.stale_window) / len(self.stale_window) if self.stale_window else 0.0
        inversion_ratio = sum(self.inversion_window) / len(self.inversion_window) if self.inversion_window else 0.0
        terminal_risk = (
            sum(self.terminal_risk_window) / len(self.terminal_risk_window)
            if self.terminal_risk_window
            else 0.0
        )
        source_trust_drop = (
            sum(self.source_trust_drop_window) / len(self.source_trust_drop_window)
            if self.source_trust_drop_window
            else 0.0
        )
        pace_instability = (
            sum(self.pace_instability_window) / len(self.pace_instability_window)
            if self.pace_instability_window
            else 0.0
        )
        critical_latency = (
            sum(self.critical_latencies_window) / len(self.critical_latencies_window)
            if self.critical_latencies_window
            else 0.0
        )
        return MissionState(
            tick=tick,
            active_link=self.active_link,
            satcom_health=self.links[LinkName.SATCOM].health,
            radio_health=self.links[LinkName.RADIO].health,
            lte_health=self.links[LinkName.LTE].health,
            mesh_health=self.links[LinkName.MESH].health,
            queue_depth=len(self.queue),
            critical_queue_depth=critical_depth,
            stale_ratio_window=stale_ratio,
            critical_latency_window=critical_latency,
            priority_inversion_window=inversion_ratio,
            terminal_risk_window=terminal_risk,
            source_trust_drop_window=source_trust_drop,
            pace_instability_window=pace_instability,
            current_attack=self.attack_mode,
            defense_alerted=self.blue.alert_tick is not None,
        )

    def _apply_attack(self, tick: int, attack) -> None:
        if attack.mode == AttackMode.NONE:
            self.terminal_risk_window.append(0.0)
            self.source_trust_drop_window.append(0.0)
            return
        link = self.links[attack.target_link]
        link.health = max(0.22, link.health - attack.intensity)
        link.loss_rate = min(0.35, link.loss_rate + attack.intensity * 0.18)
        link.jitter = min(9, link.jitter + int(attack.intensity * 8))
        terminal_risk = 0.28 if attack.mode == AttackMode.LINK_DEGRADATION else 0.48
        source_trust_drop = 0.18 if attack.mode == AttackMode.LINK_DEGRADATION else 0.36
        self.terminal_risk_window.append(terminal_risk)
        self.source_trust_drop_window.append(source_trust_drop)
        self.events.append(
            {
                "tick": tick,
                "event": "attack_action",
                "mode": attack.mode.value,
                "target_link": attack.target_link.value,
                "intensity": round(attack.intensity, 2),
                "rationale": attack.rationale,
            }
        )

    def _record_attack_decision(self, tick: int, state: MissionState, attack) -> None:
        observation = self.aura_trace.observe(state)
        candidate_actions = [
            {
                "action": attack.mode.value,
                "target_link": attack.target_link.value,
                "intensity": round(attack.intensity, 4),
                "duration": attack.duration,
                "eligible": attack.mode != AttackMode.NONE,
                "reason": attack.rationale,
            }
        ]
        self.aura_trace.memory.update_belief("last_attack_mode", attack.mode.value)
        self.aura_trace.memory.update_belief("last_target_link", attack.target_link.value)
        self.aura_trace.record_decision(
            tick=tick,
            policy="aura_lite_hybrid_schedule",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=[
                {
                    "tool_name": "select_attack_effect",
                    "input_summary": {
                        "scenario": self.attack_mode.value,
                        "tick": tick,
                        "active_link": state.active_link.value,
                    },
                    "output_summary": {
                        "mode": attack.mode.value,
                        "target_link": attack.target_link.value,
                    },
                    "status": "ok",
                }
            ],
            selected_action={
                "type": "attack_action" if attack.mode != AttackMode.NONE else "no_op",
                "mode": attack.mode.value,
                "target_link": attack.target_link.value,
                "intensity": round(attack.intensity, 4),
            },
            reason=attack.rationale,
            feedback={
                "closed_simulation_only": True,
                "attack_start": self.red.attack_start,
                "max_pulses": self.red.max_pulses,
            },
        )

    def _apply_defense(self, tick: int, defense: DefenseAction) -> None:
        if defense.priority_boost:
            for item in self.queue:
                if item.critical:
                    item.priority = item.base_priority + 6
                elif defense.minimum_mode and item.msg_type == MessageType.UAV_VIDEO:
                    item.priority = -1
        self.pace_instability_window.append(1.0 if defense.pace_transition else 0.0)
        if defense.alert:
            self.events.append(
                {
                    "tick": tick,
                    "event": "defense_action",
                    "active_link": defense.active_link.value,
                    "priority_boost": defense.priority_boost,
                    "minimum_mode": defense.minimum_mode,
                    "quarantine": defense.quarantine,
                    "pace_transition": defense.pace_transition,
                    "risk_score": defense.risk_score,
                    "alert": defense.alert,
                    "stale_badge": defense.stale_badge,
                }
            )

    def _record_defense_decision(self, tick: int, state: MissionState, defense: DefenseAction) -> None:
        observation = self.blue_trace.observe(state)
        candidate_actions = [
            {
                "action": "priority_boost",
                "selected": defense.priority_boost,
                "reason": "critical traffic protection",
            },
            {
                "action": "minimum_mode",
                "selected": defense.minimum_mode,
                "reason": "shed or compress noncritical load under risk",
            },
            {
                "action": "stale_badge",
                "selected": defense.stale_badge,
                "reason": "mark stale COP data as lower trust",
            },
            {
                "action": "pace_transition",
                "selected": defense.pace_transition,
                "target_link": defense.active_link.value,
                "reason": "select resilient PACE path",
            },
            {
                "action": "quarantine",
                "selected": defense.quarantine,
                "reason": "source or terminal trust pressure",
            },
        ]
        selected_flags = [item["action"] for item in candidate_actions if item["selected"]]
        self.blue_trace.memory.update_belief("last_risk_score", defense.risk_score)
        self.blue_trace.memory.update_belief("last_active_link", defense.active_link.value)
        self.blue_trace.record_decision(
            tick=tick,
            policy=f"{self.defense_mode}_risk_fusion",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=[
                {
                    "tool_name": "fuse_mission_risk",
                    "input_summary": observation["signals"],
                    "output_summary": {"risk_score": defense.risk_score},
                    "status": "ok",
                },
                {
                    "tool_name": "select_pace_link",
                    "input_summary": {"active_link": state.active_link.value},
                    "output_summary": {"active_link": defense.active_link.value},
                    "status": "ok",
                },
            ],
            selected_action={
                "type": "defense_action" if selected_flags or defense.alert else "no_op",
                "actions": selected_flags,
                "active_link": defense.active_link.value,
                "risk_score": defense.risk_score,
                "alert": defense.alert,
            },
            reason=defense.alert or "monitoring state; no defense action required",
            feedback={
                "detection_tick": self.blue.alert_tick,
                "recovery_tick": self.blue.recovery_tick,
                "closed_simulation_only": True,
            },
        )

    def _rule_defense_action(self, tick: int, state: MissionState) -> DefenseAction:
        degraded = state.satcom_health < 0.45
        critical_delay = state.critical_latency_window > 10.0
        stale_pressure = state.stale_ratio_window > 0.35
        risk_score = min(
            1.0,
            0.55 * max(0.0, 1.0 - state.satcom_health)
            + 0.25 * min(1.0, state.critical_latency_window / 14.0)
            + 0.20 * min(1.0, state.stale_ratio_window / 0.45),
        )
        alert = None
        if degraded or critical_delay:
            if self.blue.alert_tick is None:
                self.blue.alert_tick = tick
            alert = "rule alert: link degradation" if degraded else "rule alert: critical latency"

        active_link = state.active_link
        if degraded and state.radio_health > 0.70:
            active_link = LinkName.RADIO

        if self.blue.alert_tick is not None and self.blue.recovery_tick is None:
            recovered = not degraded and not critical_delay and state.queue_depth < 8
            if recovered:
                self.blue.stable_ticks += 1
                if self.blue.stable_ticks >= 5:
                    self.blue.recovery_tick = tick
            else:
                self.blue.stable_ticks = 0

        return DefenseAction(
            active_link=active_link,
            priority_boost=degraded or critical_delay,
            minimum_mode=degraded and (critical_delay or stale_pressure),
            alert=alert,
            stale_badge=stale_pressure,
            risk_score=round(risk_score, 4),
            quarantine=False,
            pace_transition=active_link != state.active_link,
        )

    def _process_queue(self, tick: int, attack_mode: AttackMode, defense: DefenseAction) -> None:
        link = self.links[self.active_link]
        capacity = link.effective_capacity()
        used = 0
        ordered = sorted(
            self.queue,
            key=lambda item: self._effective_priority(item, attack_mode, defense, tick),
            reverse=True,
        )
        self.queue = deque()
        delivered_this_tick: list[MissionMessage] = []

        for item in ordered:
            if defense.minimum_mode and item.msg_type == MessageType.UAV_VIDEO:
                used = self._compress_or_defer_video(tick, item, attack_mode, link, used, capacity)
                continue
            if used + item.size_kb > capacity:
                self.queue.append(item)
                continue
            used += item.size_kb
            if self.rng.random() < link.loss_rate:
                self.events.append(self._event(tick, item, "lost", attack_mode, latency=None))
                continue
            delivered_this_tick.append(item)

        noncritical_delivered_before_critical = False
        for item in delivered_this_tick:
            latency = tick - item.created_tick + link.base_latency + self.rng.randint(0, link.jitter)
            stale = latency > item.stale_after
            inversion = self._priority_inversion(item) or (item.critical and noncritical_delivered_before_critical)
            event = self._event(tick, item, "delivered", attack_mode, latency, stale, inversion)
            self.events.append(event)
            self.stale_window.append(stale)
            self.inversion_window.append(inversion)
            if item.critical:
                self.critical_latencies_window.append(latency)
            else:
                noncritical_delivered_before_critical = True
                self.max_noncritical_created_delivered = max(
                    self.max_noncritical_created_delivered,
                    item.created_tick,
                )

    @staticmethod
    def _effective_priority(
        item: MissionMessage,
        attack_mode: AttackMode,
        defense: DefenseAction,
        tick: int,
    ) -> int:
        priority = item.priority
        age = tick - item.created_tick
        slack = item.stale_after - age
        if attack_mode in {AttackMode.MISSION_AWARE_DELAY, AttackMode.FAILOVER_CHASING}:
            if item.critical and not defense.priority_boost:
                priority -= 5
            elif item.msg_type == MessageType.UAV_VIDEO:
                priority += 12
            elif not item.critical:
                priority += 3
        if defense.priority_boost and item.critical:
            priority += 8
            if slack <= 1:
                priority += 10
            elif slack <= 3:
                priority += 6
        elif item.critical and slack <= 1:
            priority += 3
        if defense.minimum_mode and item.msg_type == MessageType.UAV_VIDEO:
            priority -= 20
        return priority

    def _compress_or_defer_video(
        self,
        tick: int,
        item: MissionMessage,
        attack_mode: AttackMode,
        link: LinkState,
        used: int,
        capacity: int,
    ) -> int:
        compressed_size_kb = 85
        if used + compressed_size_kb <= capacity and self.rng.random() >= link.loss_rate:
            latency = tick - item.created_tick + link.base_latency + self.rng.randint(0, link.jitter) + 1
            self.events.append(
                {
                    **self._event(
                        tick,
                        item,
                        "compressed",
                        attack_mode,
                        latency=latency,
                        stale=latency > item.stale_after,
                        priority_inversion=False,
                    ),
                    "compressed_size_kb": compressed_size_kb,
                    "original_size_kb": item.size_kb,
                    "compression_ratio": round(compressed_size_kb / item.size_kb, 4),
                }
            )
            self.stale_window.append(latency > item.stale_after)
            self.max_noncritical_created_delivered = max(
                self.max_noncritical_created_delivered,
                item.created_tick,
            )
            return used + compressed_size_kb
        self._drop_or_keep_video(tick, item, attack_mode)
        return used

    def _drop_or_keep_video(self, tick: int, item: MissionMessage, attack_mode: AttackMode) -> None:
        if self.rng.random() < 0.7:
            self.events.append(self._event(tick, item, "deferred", attack_mode, latency=None))
        else:
            self.queue.append(item)

    def _shed_expired_noncritical(self, tick: int) -> None:
        retained: deque[MissionMessage] = deque()
        for item in self.queue:
            age = tick - item.created_tick
            if not item.critical and age > item.stale_after:
                self.events.append(
                    {
                        **self._event(
                            tick,
                            item,
                            "shed",
                            self.attack_mode,
                            latency=age,
                            stale=True,
                            priority_inversion=False,
                        ),
                        "expired": True,
                        "planned_shedding": True,
                    }
                )
            else:
                retained.append(item)
        self.queue = retained

    def _priority_inversion(self, item: MissionMessage) -> bool:
        if not item.critical:
            return False
        return self.max_noncritical_created_delivered > item.created_tick

    def _event(
        self,
        tick: int,
        item: MissionMessage,
        event: str,
        attack_mode: AttackMode,
        latency: int | None,
        stale: bool = False,
        priority_inversion: bool = False,
    ) -> dict[str, Any]:
        return {
            "tick": tick,
            "event": event,
            "msg_id": item.msg_id,
            "msg_type": item.msg_type.value,
            "source": item.source,
            "critical": item.critical,
            "active_link": self.active_link.value,
            "attack_mode": attack_mode.value,
            "latency": latency,
            "stale": stale,
            "priority_inversion": priority_inversion,
        }

    def _recover_links(self) -> None:
        for link in self.links.values():
            link.health = min(1.0, link.health + 0.045)
            defaults = {
                LinkName.SATCOM: (0.02, 2),
                LinkName.RADIO: (0.03, 1),
                LinkName.LTE: (0.05, 2),
                LinkName.MESH: (0.04, 2),
            }
            base_loss, base_jitter = defaults[link.name]
            link.loss_rate = max(base_loss, link.loss_rate - 0.012)
            link.jitter = max(base_jitter, link.jitter - 1)

    def _flush_backlog(self, tick: int) -> None:
        while self.queue:
            item = self.queue.popleft()
            latency = tick - item.created_tick
            self.events.append(
                {
                    **self._event(
                        tick,
                        item,
                        "backlog",
                        self.attack_mode,
                        latency=latency,
                        stale=latency > item.stale_after,
                        priority_inversion=False,
                    ),
                    "expired": latency > item.stale_after,
                }
            )


def write_result(result: SimulationResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / f"{result.name}_events.jsonl").open("w", encoding="utf-8") as f:
        for event in result.events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    for agent_name, traces in result.traces.items():
        with (output_dir / f"{result.name}_{agent_name}_decision_traces.jsonl").open("w", encoding="utf-8") as f:
            for trace in traces:
                f.write(json.dumps(trace, ensure_ascii=False) + "\n")
