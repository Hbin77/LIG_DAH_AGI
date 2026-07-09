from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.runtime import AgentRuntime
from src.agents.schema import ToolCallRecord
from src.shared.schemas import DefenseEvent, MissionState


class RuleTSRAR:
    ACTIONS = {"priority_reroute", "video_throttle", "stale_badge", "pace_switch"}

    def __init__(self, mode: str = "full", enabled_actions: set[str] | None = None) -> None:
        self.mode = mode
        self.enabled_actions = set(enabled_actions) if enabled_actions is not None else set(self.ACTIONS)
        self.action_cooldowns: dict[str, float] = {}
        self.event_count = 0
        self.runtime = AgentRuntime(
            agent_name="TSRA-R",
            goal="minimize mission impact with bounded defensive response actions",
        )
        self.runtime.register_tool(
            "evaluate_defense_conditions",
            "Evaluate priority, stale-data, queue, and SATCOM degradation conditions",
            self._evaluate_conditions,
        )
        self.runtime.register_tool(
            "select_fallback_link",
            "Select the best available fallback link for PACE switching",
            self._best_fallback_link,
        )
        self.runtime.register_tool(
            "summarize_attack_context",
            "Summarize recent AURA attack events for TSRA-R defense context",
            self._summarize_attack_context,
        )

    def bind_runtime(self, trace_path: Path) -> None:
        self.runtime.bind_trace_log(trace_path)

    def _ready(self, action: str, now: float, cooldown: float) -> bool:
        last = self.action_cooldowns.get(action, -10_000.0)
        return now - last >= cooldown

    def _enabled(self, action: str) -> bool:
        return action in self.enabled_actions

    def _event(self, state: MissionState, action: str, details: dict) -> DefenseEvent:
        self.event_count += 1
        self.action_cooldowns[action] = state.time_sec
        return DefenseEvent(
            event_id=f"def-{self.event_count:05d}",
            time_sec=state.time_sec,
            action=action,
            details=details,
        )

    def decide(self, state: MissionState) -> list[DefenseEvent]:
        observation = self.runtime.observe(state)
        tool_calls: list[ToolCallRecord] = []
        extra_feedback = self._before_decide(state, tool_calls)
        conditions = self.runtime.call_tool(
            "evaluate_defense_conditions",
            tool_calls,
            state=state,
        )
        attack_context = self.runtime.call_tool(
            "summarize_attack_context",
            tool_calls,
            state=state,
        )
        self._update_attack_context_belief(attack_context)
        candidate_actions: list[dict] = []
        event_requests: list[tuple[float, str, dict]] = []
        now = state.time_sec

        priority_reroute_priority = self._defense_priority_score(
            "priority_reroute",
            conditions,
            attack_context,
        )
        candidate_actions.append(
            {
                "action": "priority_reroute",
                "enabled": self._enabled("priority_reroute"),
                "eligible": conditions["priority_reroute_needed"],
                "ready": conditions["priority_reroute_ready"],
                "reason": "critical traffic waiting behind video load",
                **priority_reroute_priority,
                **self._adaptive_candidate_context("priority_reroute", extra_feedback),
                **self._cross_agent_candidate_context("priority_reroute", attack_context),
            }
        )
        if (
            self._enabled("priority_reroute")
            and conditions["priority_reroute_needed"]
            and conditions["priority_reroute_ready"]
        ):
            event_requests.append(
                (
                    priority_reroute_priority["score"],
                    "priority_reroute",
                    {
                        "until_sec": now + 70,
                        "reason": "critical traffic waiting behind video load",
                        "related_attack_context": self._compact_attack_context(attack_context),
                        **self._event_priority_details(priority_reroute_priority),
                    },
                )
            )

        video_throttle_priority = self._defense_priority_score(
            "video_throttle",
            conditions,
            attack_context,
        )
        candidate_actions.append(
            {
                "action": "video_throttle",
                "enabled": self._enabled("video_throttle"),
                "eligible": conditions["video_throttle_needed"],
                "ready": conditions["video_throttle_ready"],
                "reason": "protect critical traffic capacity",
                **video_throttle_priority,
                **self._adaptive_candidate_context("video_throttle", extra_feedback),
                **self._cross_agent_candidate_context("video_throttle", attack_context),
            }
        )
        if (
            self._enabled("video_throttle")
            and conditions["video_throttle_needed"]
            and conditions["video_throttle_ready"]
        ):
            event_requests.append(
                (
                    video_throttle_priority["score"],
                    "video_throttle",
                    {
                        "until_sec": now + 60,
                        "reason": "protect critical traffic capacity",
                        "related_attack_context": self._compact_attack_context(attack_context),
                        **self._event_priority_details(video_throttle_priority),
                    },
                )
            )

        stale_badge_priority = self._defense_priority_score(
            "stale_badge",
            conditions,
            attack_context,
        )
        candidate_actions.append(
            {
                "action": "stale_badge",
                "enabled": self._enabled("stale_badge"),
                "eligible": conditions["stale_badge_needed"],
                "ready": conditions["stale_badge_ready"],
                "reason": "mark stale COP objects as lower trust",
                **stale_badge_priority,
                **self._adaptive_candidate_context("stale_badge", extra_feedback),
                **self._cross_agent_candidate_context("stale_badge", attack_context),
            }
        )
        if (
            self._enabled("stale_badge")
            and conditions["stale_badge_needed"]
            and conditions["stale_badge_ready"]
        ):
            event_requests.append(
                (
                    stale_badge_priority["score"],
                    "stale_badge",
                    {
                        "until_sec": now + 90,
                        "stale_ratio": state.stale_data_ratio,
                        "related_attack_context": self._compact_attack_context(attack_context),
                        **self._event_priority_details(stale_badge_priority),
                    },
                )
            )

        if self.mode != "full":
            events = self._materialize_prioritized_events(state, event_requests)
            self._record_decision(
                state,
                observation,
                candidate_actions,
                tool_calls,
                events,
                extra_feedback=extra_feedback,
                attack_context=attack_context,
            )
            return events

        pace_switch_priority = self._defense_priority_score(
            "pace_switch",
            conditions,
            attack_context,
        )
        candidate_actions.append(
            {
                "action": "pace_switch",
                "enabled": self._enabled("pace_switch"),
                "eligible": conditions["pace_switch_needed"],
                "ready": conditions["pace_switch_ready"],
                "reason": conditions["pace_switch_reason"],
                **pace_switch_priority,
                **self._adaptive_candidate_context("pace_switch", extra_feedback),
                **self._cross_agent_candidate_context("pace_switch", attack_context),
            }
        )
        if (
            self._enabled("pace_switch")
            and conditions["pace_switch_needed"]
            and conditions["pace_switch_ready"]
        ):
            target = self.runtime.call_tool(
                "select_fallback_link",
                tool_calls,
                state=state,
            )
            if target:
                event_requests.append(
                    (
                        pace_switch_priority["score"],
                        "pace_switch",
                        {
                            "target_link": target,
                            "until_sec": now + 100,
                            "move_critical": True,
                            "reason": conditions["pace_switch_reason"],
                            "related_attack_context": self._compact_attack_context(attack_context),
                            **self._event_priority_details(pace_switch_priority),
                        },
                    )
                )

        events = self._materialize_prioritized_events(state, event_requests)
        self._record_decision(
            state,
            observation,
            candidate_actions,
            tool_calls,
            events,
            extra_feedback=extra_feedback,
            attack_context=attack_context,
        )
        return events

    def _before_decide(
        self,
        state: MissionState,
        tool_calls: list[ToolCallRecord],
    ) -> dict:
        return {}

    @staticmethod
    def _adaptive_candidate_context(action: str, extra_feedback: dict | None) -> dict:
        if not extra_feedback:
            return {}
        policy = extra_feedback.get("adaptive_policy")
        if not isinstance(policy, dict):
            return {}
        decision = (policy.get("action_decisions") or {}).get(action)
        if not isinstance(decision, dict):
            return {}
        return {
            "adaptive_enabled": bool(decision.get("adaptive_enabled")),
            "adaptive_gate_class": decision.get("gate_class", ""),
            "adaptive_gate_reason": decision.get("reason", ""),
            "adaptive_memory_evidence": decision.get("memory_evidence", {}),
        }

    @staticmethod
    def _summarize_attack_context(state: MissionState) -> dict:
        active_types = list(state.active_attack_types)
        recent_ids = list(state.recent_attack_event_ids)
        return {
            "active_attack_count": state.active_attack_count,
            "active_attack_types": active_types,
            "active_attack_targets": list(state.active_attack_targets),
            "recent_attack_event_ids": recent_ids,
            "recent_attack_types": list(state.recent_attack_types),
            "recent_attack_targets": list(state.recent_attack_targets),
            "last_attack_time_sec": state.last_attack_time_sec,
            "last_attack_type": state.last_attack_type,
            "last_attack_target": state.last_attack_target,
            "attack_context_seen": bool(
                state.active_attack_count > 0 or recent_ids or state.last_attack_type
            ),
        }

    def _update_attack_context_belief(self, attack_context: dict) -> None:
        self.runtime.memory.update_belief("attack_context", attack_context)
        self.runtime.memory.update_belief(
            "attack_context_seen",
            bool(attack_context.get("attack_context_seen")),
        )

    def _cross_agent_candidate_context(self, action: str, attack_context: dict) -> dict:
        return {
            "cross_agent_attack_context": attack_context,
            "cross_agent_attack_context_used": self._attack_context_relevant(
                action,
                attack_context,
            ),
        }

    def _defense_priority_score(
        self,
        action: str,
        conditions: dict[str, Any],
        attack_context: dict,
    ) -> dict:
        needed = bool(conditions.get(f"{action}_needed"))
        ready = bool(conditions.get(f"{action}_ready"))
        enabled = self._enabled(action)
        base_scores = {
            "priority_reroute": 0.82,
            "stale_badge": 0.78,
            "pace_switch": 0.72,
            "video_throttle": 0.58,
        }
        base_score = base_scores.get(action, 0.40) if enabled and needed else 0.0
        if base_score and not ready:
            base_score *= 0.25
        attack_bonus, attack_reason = self._attack_context_priority_bonus(
            action,
            attack_context,
        )
        score = base_score + attack_bonus if enabled and needed else 0.0
        return {
            "score": round(score, 6),
            "defense_base_score": round(base_score, 6),
            "attack_context_bonus": round(attack_bonus if enabled and needed else 0.0, 6),
            "attack_context_score_reason": (
                attack_reason if enabled and needed else "not_eligible_for_attack_context_bonus"
            ),
        }

    @staticmethod
    def _attack_context_priority_bonus(action: str, attack_context: dict) -> tuple[float, str]:
        active_types = set(attack_context.get("active_attack_types") or [])
        recent_types = set(attack_context.get("recent_attack_types") or [])
        types = active_types | recent_types
        if action == "priority_reroute" and types.intersection(
            {"queue_pressure", "critical_window_degradation"}
        ):
            return 0.12, "counter_queue_pressure_priority_reroute"
        if action == "video_throttle" and types.intersection(
            {"queue_pressure", "bandwidth_limit"}
        ):
            return 0.08, "counter_video_queue_pressure"
        if action == "stale_badge" and "stale_cop_induction" in types:
            return 0.12, "counter_stale_cop_induction"
        if action == "pace_switch" and types.intersection(
            {
                "link_degradation",
                "bandwidth_limit",
                "failover_chasing",
                "critical_window_degradation",
            }
        ):
            return 0.10, "counter_link_or_failover_attack"
        if attack_context.get("attack_context_seen"):
            return 0.0, "attack_context_observed_no_score_change"
        return 0.0, "no_attack_context"

    @staticmethod
    def _event_priority_details(priority: dict) -> dict:
        return {
            "defense_priority_score": priority["score"],
            "defense_base_score": priority["defense_base_score"],
            "attack_context_bonus": priority["attack_context_bonus"],
            "attack_context_score_reason": priority["attack_context_score_reason"],
        }

    def _materialize_prioritized_events(
        self,
        state: MissionState,
        event_requests: list[tuple[float, str, dict]],
    ) -> list[DefenseEvent]:
        ordered = sorted(event_requests, key=lambda item: (-item[0], item[1]))
        return [self._event(state, action, details) for _, action, details in ordered]

    @staticmethod
    def _attack_context_relevant(action: str, attack_context: dict) -> bool:
        active_types = set(attack_context.get("active_attack_types") or [])
        recent_types = set(attack_context.get("recent_attack_types") or [])
        types = active_types | recent_types
        if action in {"priority_reroute", "video_throttle"}:
            return bool(types.intersection({"queue_pressure", "critical_window_degradation", "bandwidth_limit"}))
        if action == "stale_badge":
            return "stale_cop_induction" in types
        if action == "pace_switch":
            return bool(types.intersection({"link_degradation", "bandwidth_limit", "failover_chasing", "critical_window_degradation"}))
        return bool(types)

    @staticmethod
    def _compact_attack_context(attack_context: dict) -> dict:
        return {
            "active_attack_count": attack_context.get("active_attack_count", 0),
            "active_attack_types": list(attack_context.get("active_attack_types") or []),
            "recent_attack_event_ids": list(attack_context.get("recent_attack_event_ids") or []),
            "last_attack_type": attack_context.get("last_attack_type", ""),
            "last_attack_target": attack_context.get("last_attack_target", ""),
        }

    def _evaluate_conditions(self, state: MissionState) -> dict[str, Any]:
        now = state.time_sec
        active = state.links[state.active_link]
        satcom_link_bad = (
            state.active_link == "SATCOM"
            and (
                active.base_latency_ms > 1100
                or active.loss_rate > 0.055
                or state.total_queue_kb > 4500
            )
        )
        fallback_link_bad = (
            state.active_link != "SATCOM"
            and (
                active.base_latency_ms > 550
                or active.loss_rate > 0.04
                or state.total_queue_kb > 6500
            )
        )
        initial_pace_pressure = (
            state.critical_pending > 0
            or state.recent_p95_critical_latency_sec >= 5.0
            or state.priority_inversion_rate >= 0.08
            or state.total_queue_kb > 4500
        )
        fallback_pace_pressure = (
            state.critical_pending > 0
            and (
                state.recent_p95_critical_latency_sec >= 5.0
                or state.priority_inversion_rate >= 0.08
                or active.base_latency_ms > 700
                or active.loss_rate > 0.04
            )
        )
        pace_switch_needed = (
            satcom_link_bad
            and initial_pace_pressure
        ) or (
            fallback_link_bad
            and fallback_pace_pressure
        )
        if fallback_link_bad:
            pace_switch_reason = (
                "fallback link degraded beyond mission threshold"
                if fallback_pace_pressure
                else "fallback link degraded but no critical mission pressure for reselection"
            )
        elif satcom_link_bad:
            pace_switch_reason = (
                "SATCOM degraded beyond mission threshold"
                if initial_pace_pressure
                else "SATCOM degraded but mission pressure below switch threshold"
            )
        else:
            pace_switch_reason = "active link remains within PACE threshold"
        return {
            "priority_reroute_needed": state.critical_pending > 0 and state.video_queue_kb > 500,
            "priority_reroute_ready": self._ready("priority_reroute", now, 25),
            "video_throttle_needed": state.video_queue_kb > 1500,
            "video_throttle_ready": self._ready("video_throttle", now, 35),
            "stale_badge_needed": state.stale_data_ratio > 0.25,
            "stale_badge_ready": self._ready("stale_badge", now, 30),
            "pace_switch_needed": pace_switch_needed,
            "pace_switch_ready": self._ready("pace_switch", now, 80),
            "pace_switch_reason": pace_switch_reason,
            "initial_pace_pressure": initial_pace_pressure,
            "fallback_pace_pressure": fallback_pace_pressure,
        }

    def _record_decision(
        self,
        state: MissionState,
        observation,
        candidate_actions: list[dict],
        tool_calls: list[ToolCallRecord],
        events: list[DefenseEvent],
        extra_feedback: dict | None = None,
        attack_context: dict | None = None,
    ) -> None:
        if events:
            reason = f"emitted {len(events)} defense event(s)"
            selected_action = {
                "type": "defense_events",
                "events": [
                    {
                        "event_id": event.event_id,
                        "action": event.action,
                        "details": event.details,
                    }
                    for event in events
                ],
            }
        else:
            reason = "no defense action emitted"
            selected_action = {"type": "no_op"}

        self.runtime.memory.update_belief("event_count", self.event_count)
        self.runtime.memory.update_belief("mode", self.mode)
        self.runtime.memory.update_belief("enabled_actions", sorted(self.enabled_actions))
        self.runtime.memory.update_belief("action_cooldowns", dict(self.action_cooldowns))
        if attack_context is not None:
            self._update_attack_context_belief(attack_context)
        feedback = {
            "mode": self.mode,
            "enabled_actions": sorted(self.enabled_actions),
            "event_count": self.event_count,
            "action_cooldowns": dict(self.action_cooldowns),
        }
        if attack_context is not None:
            feedback["attack_context"] = attack_context
        if extra_feedback:
            feedback.update(extra_feedback)

        self.runtime.record_decision(
            time_sec=state.time_sec,
            policy=f"rule_defense_{self.mode}",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action=selected_action,
            reason=reason,
            feedback=feedback,
        )

    @staticmethod
    def _best_fallback_link(state: MissionState) -> str | None:
        candidates = []
        for name, link in state.links.items():
            if name in {"SATCOM", state.active_link} or not link.available:
                continue
            score = link.bandwidth_mbps / max(link.base_latency_ms / 1000.0, 0.1)
            score -= 5.0 * link.loss_rate
            candidates.append((score, name))
        if not candidates:
            return None
        return max(candidates, key=lambda item: item[0])[1]
