from __future__ import annotations

from src.agents.schema import ToolCallRecord
from src.shared.schemas import MissionState
from src.tsra_r.rule_defender import RuleTSRAR


class AdaptiveTSRAR(RuleTSRAR):
    def __init__(self, mode: str = "full", memory_window: int = 3) -> None:
        super().__init__(mode=mode)
        self.memory_window = memory_window
        self.runtime.agent_name = "TSRA-R-ADAPTIVE"
        self.runtime.goal = (
            "minimize mission impact using memory-gated defensive response actions"
        )
        self.runtime.register_tool(
            "update_adaptive_action_policy",
            "Use recent AgentMemory observations to gate optional defense actions",
            self._adaptive_action_policy,
        )

    def _before_decide(
        self,
        state: MissionState,
        tool_calls: list[ToolCallRecord],
    ) -> dict:
        policy = self.runtime.call_tool(
            "update_adaptive_action_policy",
            tool_calls,
            state=state,
        )
        self.enabled_actions = set(policy["enabled_actions"])
        self.runtime.memory.update_belief("adaptive_policy", policy)
        return {"adaptive_policy": policy}

    def _adaptive_action_policy(self, state: MissionState) -> dict:
        recent = self._recent_signal_windows(state)
        critical_video_pressure = sum(
            1
            for signal in recent
            if signal["critical_pending"] > 0
            and (
                signal["video_queue_kb"] > 1000
                or signal["priority_inversion_rate"] > 0.08
            )
        )
        satcom_degradation = sum(1 for signal in recent if signal["satcom_bad"])
        severe_queue_pressure = max(signal["total_queue_kb"] for signal in recent) > 9000

        enabled = {"priority_reroute", "stale_badge"}
        action_decisions = {
            "priority_reroute": self._action_decision(
                enabled=True,
                gate_class="core_always_on",
                reason="priority_reroute kept enabled because ablation showed it protects priority ordering",
                critical_video_pressure=critical_video_pressure,
                satcom_degradation=satcom_degradation,
                severe_queue_pressure=severe_queue_pressure,
            ),
            "stale_badge": self._action_decision(
                enabled=True,
                gate_class="core_always_on",
                reason="stale_badge kept enabled because ablation showed it reduces trusted stale exposure",
                critical_video_pressure=critical_video_pressure,
                satcom_degradation=satcom_degradation,
                severe_queue_pressure=severe_queue_pressure,
            ),
        }

        if critical_video_pressure >= 2:
            enabled.add("video_throttle")
            action_decisions["video_throttle"] = self._action_decision(
                enabled=True,
                gate_class="optional_memory_enabled",
                reason="video_throttle enabled after repeated critical/video pressure in memory",
                critical_video_pressure=critical_video_pressure,
                satcom_degradation=satcom_degradation,
                severe_queue_pressure=severe_queue_pressure,
            )
        else:
            action_decisions["video_throttle"] = self._action_decision(
                enabled=False,
                gate_class="optional_memory_held",
                reason="video_throttle held back until memory shows repeated critical/video pressure",
                critical_video_pressure=critical_video_pressure,
                satcom_degradation=satcom_degradation,
                severe_queue_pressure=severe_queue_pressure,
            )

        if satcom_degradation >= 2 and severe_queue_pressure:
            enabled.add("pace_switch")
            action_decisions["pace_switch"] = self._action_decision(
                enabled=True,
                gate_class="optional_memory_enabled",
                reason="pace_switch enabled only after persistent SATCOM degradation and severe queue pressure",
                critical_video_pressure=critical_video_pressure,
                satcom_degradation=satcom_degradation,
                severe_queue_pressure=severe_queue_pressure,
            )
        else:
            action_decisions["pace_switch"] = self._action_decision(
                enabled=False,
                gate_class="optional_memory_held",
                reason="pace_switch held back to avoid premature fallback-link congestion",
                critical_video_pressure=critical_video_pressure,
                satcom_degradation=satcom_degradation,
                severe_queue_pressure=severe_queue_pressure,
            )

        return {
            "enabled_actions": sorted(enabled),
            "memory_window": self.memory_window,
            "critical_video_pressure_count": critical_video_pressure,
            "satcom_degradation_count": satcom_degradation,
            "severe_queue_pressure": severe_queue_pressure,
            "action_decisions": action_decisions,
            "reasons": [
                action_decisions[action]["reason"]
                for action in [
                    "priority_reroute",
                    "stale_badge",
                    "video_throttle",
                    "pace_switch",
                ]
            ],
        }

    @staticmethod
    def _action_decision(
        *,
        enabled: bool,
        gate_class: str,
        reason: str,
        critical_video_pressure: int,
        satcom_degradation: int,
        severe_queue_pressure: bool,
    ) -> dict:
        return {
            "adaptive_enabled": enabled,
            "gate_class": gate_class,
            "reason": reason,
            "memory_evidence": {
                "critical_video_pressure_count": critical_video_pressure,
                "satcom_degradation_count": satcom_degradation,
                "severe_queue_pressure": severe_queue_pressure,
            },
        }

    def _recent_signal_windows(self, state: MissionState) -> list[dict]:
        signals = []
        observed_history = list(self.runtime.memory.observations)
        if observed_history and observed_history[-1].time_sec == state.time_sec:
            observed_history = observed_history[:-1]

        history_limit = max(self.memory_window - 1, 0)
        history = observed_history[-history_limit:] if history_limit else []
        for observation in history:
            obs_signals = observation.signals
            links = obs_signals.get("links", {})
            active_link = observation.active_link
            active = links.get(active_link, {})
            signals.append(
                {
                    "critical_pending": float(obs_signals.get("critical_pending", 0)),
                    "video_queue_kb": float(obs_signals.get("video_queue_kb", 0.0)),
                    "total_queue_kb": float(obs_signals.get("total_queue_kb", 0.0)),
                    "priority_inversion_rate": float(
                        obs_signals.get("priority_inversion_rate", 0.0)
                    ),
                    "satcom_bad": self._link_bad(active_link, active, obs_signals),
                }
            )

        active = state.links[state.active_link]
        signals.append(
            {
                "critical_pending": float(state.critical_pending),
                "video_queue_kb": float(state.video_queue_kb),
                "total_queue_kb": float(state.total_queue_kb),
                "priority_inversion_rate": float(state.priority_inversion_rate),
                "satcom_bad": self._current_link_bad(state, active),
            }
        )
        return signals

    @staticmethod
    def _link_bad(active_link: str, active: dict, signals: dict) -> bool:
        return active_link == "SATCOM" and (
            float(active.get("latency_ms", 0.0)) > 1100
            or float(active.get("loss_rate", 0.0)) > 0.055
            or float(signals.get("total_queue_kb", 0.0)) > 4500
        )

    @staticmethod
    def _current_link_bad(state: MissionState, active) -> bool:
        return state.active_link == "SATCOM" and (
            active.base_latency_ms > 1100
            or active.loss_rate > 0.055
            or state.total_queue_kb > 4500
        )
