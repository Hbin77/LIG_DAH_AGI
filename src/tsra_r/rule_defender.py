from __future__ import annotations

from pathlib import Path

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
        conditions = self.runtime.call_tool(
            "evaluate_defense_conditions",
            tool_calls,
            state=state,
        )
        candidate_actions: list[dict] = []
        events: list[DefenseEvent] = []
        now = state.time_sec

        candidate_actions.append(
            {
                "action": "priority_reroute",
                "enabled": self._enabled("priority_reroute"),
                "eligible": conditions["priority_reroute_needed"],
                "ready": conditions["priority_reroute_ready"],
                "reason": "critical traffic waiting behind video load",
            }
        )
        if (
            self._enabled("priority_reroute")
            and conditions["priority_reroute_needed"]
            and conditions["priority_reroute_ready"]
        ):
            events.append(
                self._event(
                    state,
                    "priority_reroute",
                    {"until_sec": now + 70, "reason": "critical traffic waiting behind video load"},
                )
            )

        candidate_actions.append(
            {
                "action": "video_throttle",
                "enabled": self._enabled("video_throttle"),
                "eligible": conditions["video_throttle_needed"],
                "ready": conditions["video_throttle_ready"],
                "reason": "protect critical traffic capacity",
            }
        )
        if (
            self._enabled("video_throttle")
            and conditions["video_throttle_needed"]
            and conditions["video_throttle_ready"]
        ):
            events.append(
                self._event(
                    state,
                    "video_throttle",
                    {"until_sec": now + 60, "reason": "protect critical traffic capacity"},
                )
            )

        candidate_actions.append(
            {
                "action": "stale_badge",
                "enabled": self._enabled("stale_badge"),
                "eligible": conditions["stale_badge_needed"],
                "ready": conditions["stale_badge_ready"],
                "reason": "mark stale COP objects as lower trust",
            }
        )
        if (
            self._enabled("stale_badge")
            and conditions["stale_badge_needed"]
            and conditions["stale_badge_ready"]
        ):
            events.append(
                self._event(
                    state,
                    "stale_badge",
                    {"until_sec": now + 90, "stale_ratio": state.stale_data_ratio},
                )
            )

        if self.mode != "full":
            self._record_decision(state, observation, candidate_actions, tool_calls, events)
            return events

        candidate_actions.append(
            {
                "action": "pace_switch",
                "enabled": self._enabled("pace_switch"),
                "eligible": conditions["pace_switch_needed"],
                "ready": conditions["pace_switch_ready"],
                "reason": "SATCOM degraded beyond mission threshold",
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
                events.append(
                    self._event(
                        state,
                        "pace_switch",
                        {
                            "target_link": target,
                            "until_sec": now + 100,
                            "move_critical": True,
                            "reason": "SATCOM degraded beyond mission threshold",
                        },
                    )
                )

        self._record_decision(state, observation, candidate_actions, tool_calls, events)
        return events

    def _evaluate_conditions(self, state: MissionState) -> dict[str, bool]:
        now = state.time_sec
        active = state.links[state.active_link]
        satcom_bad = (
            state.active_link == "SATCOM"
            and (
                active.base_latency_ms > 1100
                or active.loss_rate > 0.055
                or state.total_queue_kb > 4500
            )
        )
        return {
            "priority_reroute_needed": state.critical_pending > 0 and state.video_queue_kb > 500,
            "priority_reroute_ready": self._ready("priority_reroute", now, 25),
            "video_throttle_needed": state.video_queue_kb > 1500,
            "video_throttle_ready": self._ready("video_throttle", now, 35),
            "stale_badge_needed": state.stale_data_ratio > 0.25,
            "stale_badge_ready": self._ready("stale_badge", now, 30),
            "pace_switch_needed": satcom_bad,
            "pace_switch_ready": self._ready("pace_switch", now, 80),
        }

    def _record_decision(
        self,
        state: MissionState,
        observation,
        candidate_actions: list[dict],
        tool_calls: list[ToolCallRecord],
        events: list[DefenseEvent],
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
        self.runtime.record_decision(
            time_sec=state.time_sec,
            policy=f"rule_defense_{self.mode}",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action=selected_action,
            reason=reason,
            feedback={
                "mode": self.mode,
                "enabled_actions": sorted(self.enabled_actions),
                "event_count": self.event_count,
                "action_cooldowns": dict(self.action_cooldowns),
            },
        )

    @staticmethod
    def _best_fallback_link(state: MissionState) -> str | None:
        candidates = []
        for name, link in state.links.items():
            if name == "SATCOM" or not link.available:
                continue
            score = link.bandwidth_mbps / max(link.base_latency_ms / 1000.0, 0.1)
            score -= 5.0 * link.loss_rate
            candidates.append((score, name))
        if not candidates:
            return None
        return max(candidates, key=lambda item: item[0])[1]
