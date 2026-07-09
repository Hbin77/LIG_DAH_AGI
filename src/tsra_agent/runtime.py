from __future__ import annotations

from collections import deque
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


class AgentMemory:
    """Small runtime memory used to make agent decisions auditable."""

    def __init__(self, max_observations: int = 24, max_decisions: int = 24) -> None:
        self.observations: deque[dict[str, Any]] = deque(maxlen=max_observations)
        self.decisions: deque[dict[str, Any]] = deque(maxlen=max_decisions)
        self.belief_state: dict[str, Any] = {}

    def remember_observation(self, observation: dict[str, Any]) -> None:
        self.observations.append(observation)

    def remember_decision(self, decision: dict[str, Any]) -> None:
        self.decisions.append(decision)

    def update_belief(self, key: str, value: Any) -> None:
        self.belief_state[key] = to_plain(value)

    def summary(self) -> dict[str, Any]:
        return {
            "recent_observation_count": len(self.observations),
            "recent_decision_count": len(self.decisions),
            "belief_state": to_plain(self.belief_state),
        }


class AgentTraceRecorder:
    """Records observe-memory-candidate-decision-feedback loops as JSON-ready dicts."""

    def __init__(self, agent_name: str, goal: str) -> None:
        self.agent_name = agent_name
        self.goal = goal
        self.memory = AgentMemory()
        self.traces: list[dict[str, Any]] = []

    def observe(self, state: Any) -> dict[str, Any]:
        observation = {
            "agent": self.agent_name,
            "tick": state.tick,
            "active_link": enum_value(state.active_link),
            "signals": {
                "satcom_health": round(state.satcom_health, 4),
                "radio_health": round(state.radio_health, 4),
                "lte_health": round(state.lte_health, 4),
                "mesh_health": round(state.mesh_health, 4),
                "queue_depth": state.queue_depth,
                "critical_queue_depth": state.critical_queue_depth,
                "stale_ratio_window": round(state.stale_ratio_window, 4),
                "critical_latency_window": round(state.critical_latency_window, 4),
                "priority_inversion_window": round(state.priority_inversion_window, 4),
                "terminal_risk_window": round(state.terminal_risk_window, 4),
                "source_trust_drop_window": round(state.source_trust_drop_window, 4),
                "pace_instability_window": round(state.pace_instability_window, 4),
                "current_attack": enum_value(state.current_attack),
                "defense_alerted": state.defense_alerted,
            },
        }
        self.memory.remember_observation(observation)
        return observation

    def record_decision(
        self,
        *,
        tick: int,
        policy: str,
        observation: dict[str, Any],
        candidate_actions: list[dict[str, Any]],
        selected_action: dict[str, Any],
        reason: str,
        tool_calls: list[dict[str, Any]] | None = None,
        feedback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        trace = {
            "trace_id": f"{self.agent_name.lower().replace(' ', '-')}-{len(self.traces) + 1:05d}",
            "agent": self.agent_name,
            "tick": tick,
            "goal": self.goal,
            "policy": policy,
            "observation": observation,
            "memory": self.memory.summary(),
            "candidate_actions": to_plain(candidate_actions),
            "tool_calls": to_plain(tool_calls or []),
            "selected_action": to_plain(selected_action),
            "reason": reason,
            "feedback": to_plain(feedback or {}),
            "safety_boundary": "closed synthetic mission simulation only; no RF parameters, exploit code, or live network action",
        }
        self.traces.append(trace)
        self.memory.remember_decision(trace)
        return trace


def to_plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: to_plain(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, deque)):
        return [to_plain(item) for item in value]
    return value


def enum_value(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value
