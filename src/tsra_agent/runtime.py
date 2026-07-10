from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
import math
from pathlib import Path
import re
from typing import Any, Callable


TOOL_CALL_REQUIRED_FIELDS = {
    "tool_name",
    "purpose",
    "input_summary",
    "output_summary",
    "status",
    "safety_checked",
    "safety_check",
}


@dataclass(frozen=True)
class ToolCallResult:
    tool_name: str
    purpose: str
    input_summary: dict[str, Any]
    output_summary: dict[str, Any]
    safety_checked: bool
    safety_check: dict[str, Any]
    status: str = "ok"

    def as_trace(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "purpose": self.purpose,
            "input_summary": to_summary(self.input_summary),
            "output_summary": to_summary(self.output_summary),
            "status": self.status,
            "safety_checked": self.safety_checked,
            "safety_check": to_plain(self.safety_check),
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
        safety_validator: Callable[[str, Any], dict[str, Any]],
        allowed_input_fields: frozenset[str],
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
        self.safety_validator = safety_validator
        self.allowed_input_fields = allowed_input_fields

    def execute(self, **kwargs: Any) -> tuple[Any, dict[str, Any]]:
        provided_fields = frozenset(kwargs)
        unexpected_fields = sorted(provided_fields - self.allowed_input_fields)
        missing_fields = sorted(self.allowed_input_fields - provided_fields)
        if unexpected_fields or missing_fields:
            schema_check = {
                "check_id": "registered_tool_input_schema/v1",
                "passed": False,
                "allowed_fields": sorted(self.allowed_input_fields),
                "unexpected_fields": unexpected_fields,
                "missing_fields": missing_fields,
            }
            failed = ToolCallResult(
                tool_name=self.name,
                purpose=self.purpose,
                input_summary=to_summary(kwargs),
                output_summary={"message": "tool input fields differ from registered schema"},
                safety_checked=False,
                safety_check={
                    "check_id": "closed_synthetic_bounds/v1",
                    "input": schema_check,
                    "passed": False,
                },
                status="error",
            ).as_trace()
            validate_tool_call(failed)
            raise AgentToolExecutionError(
                f"agent tool {self.name!r} rejected unregistered input fields",
                failed,
            )
        input_summary = (
            self.input_summarizer(kwargs)
            if self.input_summarizer is not None
            else to_summary(kwargs)
        )
        input_check = self.safety_validator("input", kwargs)
        if input_check.get("passed") is not True:
            failed = ToolCallResult(
                tool_name=self.name,
                purpose=self.purpose,
                input_summary=input_summary,
                output_summary={"message": "tool input failed synthetic safety validation"},
                safety_checked=False,
                safety_check={
                    "check_id": "closed_synthetic_bounds/v1",
                    "input": input_check,
                    "passed": False,
                },
                status="error",
            ).as_trace()
            validate_tool_call(failed)
            raise AgentToolExecutionError(
                f"agent tool {self.name!r} failed input safety validation",
                failed,
            )
        try:
            output = self.handler(**kwargs)
            output_summary = (
                self.output_summarizer(output)
                if self.output_summarizer is not None
                else to_summary(output)
            )
            output_check = self.safety_validator("output", output)
            safety_check = {
                "check_id": "closed_synthetic_bounds/v1",
                "input": input_check,
                "output": output_check,
                "passed": bool(
                    input_check.get("passed") is True
                    and output_check.get("passed") is True
                ),
            }
            if not safety_check["passed"]:
                failed = ToolCallResult(
                    tool_name=self.name,
                    purpose=self.purpose,
                    input_summary=input_summary,
                    output_summary=output_summary,
                    safety_checked=False,
                    safety_check=safety_check,
                    status="error",
                ).as_trace()
                validate_tool_call(failed)
                raise AgentToolExecutionError(
                    f"agent tool {self.name!r} failed output safety validation",
                    failed,
                )
            result = ToolCallResult(
                tool_name=self.name,
                purpose=self.purpose,
                input_summary=input_summary,
                output_summary=output_summary,
                safety_checked=bool(safety_check["passed"]),
                safety_check=safety_check,
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
                safety_checked=False,
                safety_check={
                    "check_id": "closed_synthetic_bounds/v1",
                    "input": input_check,
                    "passed": False,
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

    def __init__(
        self,
        agent_name: str,
        goal: str,
        *,
        retain_traces: bool = True,
    ) -> None:
        self.agent_name = agent_name
        self.goal = goal
        self.memory = AgentMemory()
        self.retain_traces = retain_traces
        self.traces: list[dict[str, Any]] = []
        self._trace_count = 0

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

        self._trace_count += 1
        trace = {
            "trace_id": f"{slug(self.agent_name)}-{self._trace_count:05d}",
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
        if self.retain_traces:
            self.traces.append(trace)
        self.memory.remember_decision(trace)
        return trace


class AgentRuntime:
    """Owns one agent's observe-tool-decide-feedback execution lifecycle."""

    def __init__(
        self,
        agent_name: str,
        goal: str,
        *,
        retain_traces: bool = True,
    ) -> None:
        self.agent_name = agent_name
        self.goal = goal
        self.recorder = AgentTraceRecorder(
            agent_name,
            goal,
            retain_traces=retain_traces,
        )
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
        safety_validator: Callable[[str, Any], dict[str, Any]],
        allowed_input_fields: set[str] | frozenset[str],
    ) -> None:
        if name in self._tools:
            raise ValueError(f"duplicate agent tool: {name}")
        self._tools[name] = AgentTool(
            name,
            purpose,
            handler,
            input_summarizer=input_summarizer,
            output_summarizer=output_summarizer,
            safety_validator=safety_validator,
            allowed_input_fields=frozenset(allowed_input_fields),
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
    if not isinstance(tool_call["safety_check"], dict):
        raise ValueError("tool call safety_check must be a dictionary")
    if tool_call["status"] == "ok" and tool_call["safety_checked"] is not True:
        raise ValueError("synthetic agent tools must pass safety_checked=True")
    if tool_call["status"] == "ok" and tool_call["safety_check"].get("passed") is not True:
        raise ValueError("successful tool calls require a passed safety check")


def closed_synthetic_tool_validator(stage: str, payload: Any) -> dict[str, Any]:
    """Validate that a tool payload stays inside bounded synthetic mission data."""

    if stage not in {"input", "output"}:
        raise ValueError(f"unsupported safety validation stage: {stage}")
    violations: list[str] = []
    forbidden_key_tokens = {
        "shell",
        "subprocess",
        "socket",
        "endpoint",
        "host",
        "command",
        "url",
        "uri",
        "payload",
        "rf",
        "destination",
        "address",
        "ip_address",
        "frequency",
        "exploit",
        "network_action",
    }
    bounded_keys = {
        "intensity",
        "probability",
        "risk_score",
        "ml_risk",
        "heuristic_risk",
        "fused_risk",
        "satcom_health",
        "radio_health",
        "lte_health",
        "mesh_health",
    }
    integer_bounds = {
        "duration": (0, 180),
        # Rule-policy simulations may run longer than the final 180-tick AURA-ML
        # scope. The ML scope is enforced independently at construction time.
        "tick": (0, 10_000_000),
        "queue_depth": (0, 100_000),
        "critical_queue_depth": (0, 100_000),
        "candidate_count": (0, 10_000),
        "feature_count": (0, 10_000),
    }

    def visit(value: Any, path: str, key: str | None = None) -> None:
        if isinstance(value, Path) or isinstance(value, (bytes, bytearray)) or callable(value):
            violations.append(f"{path}: unsupported operational payload type")
            return
        if is_dataclass(value):
            visit(asdict(value), path, key)
            return
        if isinstance(value, Enum):
            return
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                normalized = str(child_key).lower()
                key_tokens = set(re.split(r"[^a-z0-9]+", normalized))
                if key_tokens & forbidden_key_tokens:
                    violations.append(f"{path}.{normalized}: forbidden operational field")
                visit(child_value, f"{path}.{normalized}", normalized)
            return
        if isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                visit(item, f"{path}[{index}]", key)
            return
        if isinstance(value, float) and not math.isfinite(value):
            violations.append(f"{path}: non-finite numeric value")
        if isinstance(value, str):
            lowered = value.lower()
            unsafe_string_patterns = {
                "URL": r"(?:https?|ftp)://",
                "IP address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                "RF parameter": r"\b\d+(?:\.\d+)?\s*(?:hz|khz|mhz|ghz)\b",
                "shell command": r"(?:rm\s+-rf|/bin/|powershell|subprocess)",
                "exploit instruction": r"\bexploit(?:\s+code)?\b",
            }
            for label, pattern in unsafe_string_patterns.items():
                if re.search(pattern, lowered):
                    violations.append(f"{path}: forbidden {label} content")
        if key in bounded_keys and isinstance(value, (int, float)) and not 0.0 <= float(value) <= 1.0:
            violations.append(f"{path}: bounded value outside [0, 1]")
        if key in integer_bounds and isinstance(value, (int, float)):
            lower, upper = integer_bounds[key]
            if int(value) != value or not lower <= int(value) <= upper:
                violations.append(f"{path}: integer value outside [{lower}, {upper}]")
        if value is not None and not isinstance(value, (str, int, float, bool)):
            violations.append(f"{path}: unsupported payload type {type(value).__name__}")

    def validate_candidate_selection(value: Any, path: str) -> None:
        if is_dataclass(value):
            value = asdict(value)
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                validate_candidate_selection(child_value, f"{path}.{child_key}")
            return
        if isinstance(value, (list, tuple)):
            candidate_rows = [
                item
                for item in value
                if isinstance(item, dict) and "selected" in item
            ]
            if candidate_rows and sum(
                item.get("selected") is True for item in candidate_rows
            ) != 1:
                violations.append(
                    f"{path}: candidate set must mark exactly one selected row"
                )
            for index, item in enumerate(value):
                validate_candidate_selection(item, f"{path}[{index}]")

    visit(payload, stage)
    validate_candidate_selection(payload, stage)
    return {
        "check_id": "closed_synthetic_bounds/v1",
        "stage": stage,
        "passed": not violations,
        "violations": violations,
    }


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
