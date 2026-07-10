from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any, Callable


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
            "input_summary": to_summary(self.input_summary),
            "output_summary": to_summary(self.output_summary),
            "status": self.status,
            "safety_checked": self.safety_checked,
        }


class AgentToolExecutionError(RuntimeError):
    """Carries the failed tool-call record so the runtime remains auditable."""

    def __init__(self, message: str, tool_call: dict[str, Any]) -> None:
        super().__init__(message)
        self.tool_call = tool_call


class AgentTool:
    """Callable tool registered with an AgentRuntime.

    The handler is executed by the runtime. Input and output summaries are derived
    from that real invocation, rather than supplied after a policy already ran.
    """

    def __init__(
        self,
        name: str,
        purpose: str,
        handler: Callable[..., Any],
        *,
        input_summarizer: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        output_summarizer: Callable[[Any], dict[str, Any]] | None = None,
    ) -> None:
        if not name or not purpose:
            raise ValueError("agent tools require a non-empty name and purpose")
        if not callable(handler):
            raise TypeError("agent tool handler must be callable")
        self.name = name
        self.purpose = purpose
        self.handler = handler
        self.input_summarizer = input_summarizer
        self.output_summarizer = output_summarizer

    def execute(self, **kwargs: Any) -> tuple[Any, dict[str, Any]]:
        input_summary = (
            self.input_summarizer(kwargs)
            if self.input_summarizer is not None
            else to_summary(kwargs)
        )
        try:
            output = self.handler(**kwargs)
            output_summary = (
                self.output_summarizer(output)
                if self.output_summarizer is not None
                else to_summary(output)
            )
            result = ToolCallResult(
                tool_name=self.name,
                purpose=self.purpose,
                input_summary=input_summary,
                output_summary=output_summary,
            )
            trace = result.as_trace()
            validate_tool_call(trace)
            return output, trace
        except AgentToolExecutionError:
            raise
        except Exception as exc:
            failed = ToolCallResult(
                tool_name=self.name,
                purpose=self.purpose,
                input_summary=input_summary,
                output_summary={
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
                status="error",
            ).as_trace()
            validate_tool_call(failed)
            raise AgentToolExecutionError(
                f"agent tool {self.name!r} failed: {exc}",
                failed,
            ) from exc


class AgentMemory:
    """Bounded working memory shared by one agent runtime."""

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
        last_observation = self.observations[-1] if self.observations else None
        last_decision = self.decisions[-1] if self.decisions else None
        return {
            "recent_observation_count": len(self.observations),
            "recent_decision_count": len(self.decisions),
            "belief_state": to_plain(self.belief_state),
            "last_observed_tick": last_observation.get("tick") if last_observation else None,
            "last_selected_action": (
                to_plain(last_decision.get("selected_action"))
                if last_decision
                else None
            ),
            "last_feedback": (
                to_plain(last_decision.get("feedback"))
                if last_decision
                else None
            ),
        }


class AgentTraceRecorder:
    """Persists observe-memory-tool-candidate-decision-feedback loops."""

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
        tool_calls: list[dict[str, Any]],
        feedback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        plain_tool_calls = to_plain(tool_calls)
        for tool_call in plain_tool_calls:
            validate_tool_call(tool_call)

        trace = {
            "trace_id": f"{slug(self.agent_name)}-{len(self.traces) + 1:05d}",
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


class AgentRuntime:
    """Owns one agent's observe-tool-decide-feedback execution lifecycle."""

    def __init__(self, agent_name: str, goal: str) -> None:
        self.agent_name = agent_name
        self.goal = goal
        self.recorder = AgentTraceRecorder(agent_name, goal)
        self.memory = self.recorder.memory
        self._tools: dict[str, AgentTool] = {}
        self._phase = "idle"
        self._observation: dict[str, Any] | None = None
        self._tool_calls: list[dict[str, Any]] = []
        self._last_trace: dict[str, Any] | None = None

    @property
    def traces(self) -> list[dict[str, Any]]:
        return self.recorder.traces

    @property
    def registered_tools(self) -> list[str]:
        return sorted(self._tools)

    def register_tool(
        self,
        name: str,
        purpose: str,
        handler: Callable[..., Any],
        *,
        input_summarizer: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        output_summarizer: Callable[[Any], dict[str, Any]] | None = None,
    ) -> None:
        if name in self._tools:
            raise ValueError(f"duplicate agent tool: {name}")
        self._tools[name] = AgentTool(
            name,
            purpose,
            handler,
            input_summarizer=input_summarizer,
            output_summarizer=output_summarizer,
        )

    def begin_cycle(self, state: Any) -> dict[str, Any]:
        if self._phase != "idle":
            raise RuntimeError(f"cannot observe while runtime phase is {self._phase}")
        self._observation = self.recorder.observe(state)
        self._tool_calls = []
        self._phase = "observed"
        return self._observation

    def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        if self._phase != "observed":
            raise RuntimeError("agent tools may only run after begin_cycle")
        if tool_name not in self._tools:
            raise KeyError(f"unknown agent tool: {tool_name}")
        try:
            output, trace = self._tools[tool_name].execute(**kwargs)
            self._tool_calls.append(trace)
            return output
        except AgentToolExecutionError as exc:
            self._tool_calls.append(exc.tool_call)
            raise

    def commit_decision(
        self,
        *,
        tick: int,
        policy: str,
        candidate_actions: list[dict[str, Any]],
        selected_action: dict[str, Any],
        reason: str,
        feedback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self._phase != "observed" or self._observation is None:
            raise RuntimeError("commit_decision requires an active observed cycle")
        if not self._tool_calls:
            raise RuntimeError("an agent decision must be produced through at least one registered tool")
        if not candidate_actions:
            raise ValueError("an agent decision requires at least one candidate action")

        trace = self.recorder.record_decision(
            tick=tick,
            policy=policy,
            observation=self._observation,
            candidate_actions=candidate_actions,
            selected_action=selected_action,
            reason=reason,
            tool_calls=self._tool_calls,
            feedback={
                "feedback_status": "pending_environment",
                **(feedback or {}),
            },
        )
        trace["runtime"] = {
            "implementation": "AgentRuntime",
            "phase": "decision_committed",
            "registered_tools": self.registered_tools,
            "tool_call_count": len(self._tool_calls),
            "feedback_attached": False,
        }
        self._last_trace = trace
        self._observation = None
        self._tool_calls = []
        self._phase = "idle"
        return trace

    def attach_feedback(self, feedback: dict[str, Any]) -> None:
        if self._phase != "idle":
            raise RuntimeError("feedback may only be attached after a decision is committed")
        if self._last_trace is None:
            raise RuntimeError("cannot attach feedback before the first decision")
        self._last_trace["feedback"].update(to_plain(feedback))
        self._last_trace["feedback"]["feedback_status"] = "observed"
        self._last_trace["runtime"]["phase"] = "feedback_attached"
        self._last_trace["runtime"]["feedback_attached"] = True
        self.memory.update_belief("last_environment_feedback", feedback)


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


def to_summary(value: Any, *, max_items: int = 20) -> dict[str, Any]:
    plain = compact(value, max_items=max_items)
    if isinstance(plain, dict):
        return plain
    return {"result": plain}


def compact(value: Any, *, max_items: int = 20) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return compact(asdict(value), max_items=max_items)
    if isinstance(value, dict):
        items = list(value.items())
        result = {
            str(key): compact(item, max_items=max_items)
            for key, item in items[:max_items]
        }
        if len(items) > max_items:
            result["truncated_count"] = len(items) - max_items
        return result
    if isinstance(value, (list, tuple, set, deque)):
        items = list(value)
        result = [compact(item, max_items=max_items) for item in items[:max_items]]
        if len(items) > max_items:
            result.append({"truncated_count": len(items) - max_items})
        return result
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return str(value)


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


def slug(value: str) -> str:
    return "-".join(part for part in value.lower().replace("_", "-").split() if part)
