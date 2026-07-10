from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any


TOOL_CALL_REQUIRED_FIELDS = {
    "tool_name",
    "purpose",
    "input_summary",
    "output_summary",
    "status",
    "safety_checked",
}


@dataclass(frozen=True)
class ToolCallResult:
    tool_name: str
    purpose: str
    input_summary: dict[str, Any]
    output_summary: dict[str, Any]
    status: str = "ok"
    safety_checked: bool = True

    def as_trace(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "purpose": self.purpose,
            "input_summary": to_plain(self.input_summary),
            "output_summary": to_plain(self.output_summary),
            "status": self.status,
            "safety_checked": self.safety_checked,
        }


class AgentTool:
    """Structured synthetic tool wrapper for auditable agent action loops."""

    def __init__(self, name: str, purpose: str) -> None:
        self.name = name
        self.purpose = purpose

    def run(
        self,
        *,
        input_summary: dict[str, Any],
        output_summary: dict[str, Any],
        status: str = "ok",
        safety_checked: bool = True,
    ) -> dict[str, Any]:
        result = ToolCallResult(
            tool_name=self.name,
            purpose=self.purpose,
            input_summary=input_summary,
            output_summary=output_summary,
            status=status,
            safety_checked=safety_checked,
        )
        trace = result.as_trace()
        validate_tool_call(trace)
        return trace


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
        plain_tool_calls = to_plain(tool_calls or [])
        for tool_call in plain_tool_calls:
            validate_tool_call(tool_call)

        trace = {
            "trace_id": f"{self.agent_name.lower().replace(' ', '-')}-{len(self.traces) + 1:05d}",
            "agent": self.agent_name,
            "tick": tick,
            "goal": self.goal,
            "policy": policy,
            "observation": observation,
            "memory": self.memory.summary(),
            "candidate_actions": to_plain(candidate_actions),
            "tool_calls": plain_tool_calls,
            "selected_action": to_plain(selected_action),
            "reason": reason,
            "feedback": to_plain(feedback or {}),
            "safety_boundary": "closed synthetic mission simulation only; no RF parameters, exploit code, or live network action",
        }
        self.traces.append(trace)
        self.memory.remember_decision(trace)
        return trace


def validate_tool_call(tool_call: dict[str, Any]) -> None:
    missing = TOOL_CALL_REQUIRED_FIELDS - set(tool_call)
    if missing:
        raise ValueError(f"tool call missing fields: {sorted(missing)}")
    if tool_call["status"] not in {"ok", "skipped", "error"}:
        raise ValueError(f"invalid tool call status: {tool_call['status']}")
    if not tool_call["tool_name"] or not tool_call["purpose"]:
        raise ValueError("tool call requires non-empty tool_name and purpose")
    if not isinstance(tool_call["input_summary"], dict) or not isinstance(tool_call["output_summary"], dict):
        raise ValueError("tool call summaries must be dictionaries")
    if tool_call["safety_checked"] is not True:
        raise ValueError("synthetic agent tools must pass safety_checked=True")


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
