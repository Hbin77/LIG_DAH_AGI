from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentObservation:
    agent: str
    time_sec: float
    mission_phase: str
    active_link: str
    signals: dict[str, Any]


@dataclass
class ToolCallRecord:
    tool_name: str
    input_summary: dict[str, Any]
    output_summary: Any
    status: str = "ok"


@dataclass
class DecisionTrace:
    trace_id: str
    agent: str
    time_sec: float
    goal: str
    policy: str
    observation: dict[str, Any]
    memory: dict[str, Any]
    candidate_actions: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    selected_action: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    feedback: dict[str, Any] = field(default_factory=dict)
