from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.agents.memory import AgentMemory
from src.agents.schema import AgentObservation, DecisionTrace, ToolCallRecord
from src.agents.tools import ToolRegistry
from src.shared.event_log import JsonlLogger
from src.shared.schemas import AttackCandidate, AttackEvent, DefenseEvent, MissionState, to_plain_dict


class AgentRuntime:
    def __init__(self, agent_name: str, goal: str) -> None:
        self.agent_name = agent_name
        self.goal = goal
        self.memory = AgentMemory()
        self.tools = ToolRegistry()
        self.trace_logger: JsonlLogger | None = None
        self.trace_count = 0

    def bind_trace_log(self, path: Path) -> None:
        self.trace_logger = JsonlLogger(path)

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable[..., Any],
    ) -> None:
        self.tools.register(name, description, handler)

    def observe(self, state: MissionState) -> AgentObservation:
        observation = AgentObservation(
            agent=self.agent_name,
            time_sec=state.time_sec,
            mission_phase=state.mission_phase,
            active_link=state.active_link,
            signals={
                "total_queue_kb": round(state.total_queue_kb, 3),
                "critical_pending": state.critical_pending,
                "video_queue_kb": round(state.video_queue_kb, 3),
                "stale_data_ratio": round(state.stale_data_ratio, 4),
                "recent_p95_critical_latency_sec": round(
                    state.recent_p95_critical_latency_sec, 4
                ),
                "priority_inversion_rate": round(state.priority_inversion_rate, 4),
                "defense_mode": state.defense_mode,
                "active_attack_count": state.active_attack_count,
                "active_attack_types": list(state.active_attack_types),
                "active_attack_targets": list(state.active_attack_targets),
                "recent_attack_event_ids": list(state.recent_attack_event_ids),
                "recent_attack_types": list(state.recent_attack_types),
                "recent_attack_targets": list(state.recent_attack_targets),
                "last_attack_time_sec": state.last_attack_time_sec,
                "last_attack_type": state.last_attack_type,
                "last_attack_target": state.last_attack_target,
                "active_defense_actions": list(state.active_defense_actions),
                "recent_defense_actions": list(state.recent_defense_actions),
                "last_defense_time_sec": state.last_defense_time_sec,
                "last_defense_action": state.last_defense_action,
                "links": {
                    name: {
                        "available": link.available,
                        "bandwidth_mbps": round(link.bandwidth_mbps, 4),
                        "latency_ms": round(link.base_latency_ms, 4),
                        "jitter_ms": round(link.jitter_ms, 4),
                        "loss_rate": round(link.loss_rate, 4),
                        "queue_depth": link.queue_depth,
                    }
                    for name, link in state.links.items()
                },
            },
        )
        self.memory.remember_observation(observation)
        return observation

    def call_tool(
        self,
        tool_name: str,
        tool_calls: list[ToolCallRecord],
        **kwargs: Any,
    ) -> Any:
        tool = self.tools.get(tool_name)
        input_summary = {key: self._summarize(value) for key, value in kwargs.items()}
        try:
            result = tool.run(**kwargs)
            tool_calls.append(
                ToolCallRecord(
                    tool_name=tool_name,
                    input_summary=input_summary,
                    output_summary=self._summarize(result),
                )
            )
            return result
        except Exception as exc:
            tool_calls.append(
                ToolCallRecord(
                    tool_name=tool_name,
                    input_summary=input_summary,
                    output_summary={"error": str(exc)},
                    status="error",
                )
            )
            raise

    def record_decision(
        self,
        *,
        time_sec: float,
        policy: str,
        observation: AgentObservation,
        candidate_actions: list[dict[str, Any]],
        tool_calls: list[ToolCallRecord],
        selected_action: dict[str, Any],
        reason: str,
        feedback: dict[str, Any] | None = None,
    ) -> DecisionTrace:
        self.trace_count += 1
        trace = DecisionTrace(
            trace_id=f"{self.agent_name.lower()}-trace-{self.trace_count:05d}",
            agent=self.agent_name,
            time_sec=time_sec,
            goal=self.goal,
            policy=policy,
            observation=to_plain_dict(observation),
            memory=self.memory.summary(),
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action=selected_action,
            reason=reason,
            feedback=feedback or {},
        )
        self.memory.remember_decision(trace)
        if self.trace_logger:
            self.trace_logger.write(trace)
        return trace

    def _summarize(self, value: Any) -> Any:
        if isinstance(value, MissionState):
            return {
                "time_sec": value.time_sec,
                "mission_phase": value.mission_phase,
                "active_link": value.active_link,
                "total_queue_kb": round(value.total_queue_kb, 3),
                "critical_pending": value.critical_pending,
                "video_queue_kb": round(value.video_queue_kb, 3),
                "stale_data_ratio": round(value.stale_data_ratio, 4),
                "priority_inversion_rate": round(value.priority_inversion_rate, 4),
                "defense_mode": value.defense_mode,
                "active_attack_count": value.active_attack_count,
                "active_attack_types": list(value.active_attack_types),
                "recent_attack_event_ids": list(value.recent_attack_event_ids),
                "active_defense_actions": list(value.active_defense_actions),
                "recent_defense_actions": list(value.recent_defense_actions),
            }
        if isinstance(value, AttackCandidate):
            return {
                "attack_type": value.attack_type,
                "target_link": value.target_link,
                "target_traffic_classes": list(value.target_traffic_classes),
                "start_time": value.start_time,
                "duration_sec": value.duration_sec,
                "latency_ms_add": value.latency_ms_add,
                "jitter_ms_add": value.jitter_ms_add,
                "packet_loss_add": value.packet_loss_add,
                "bandwidth_limit_mbps": value.bandwidth_limit_mbps,
                "queue_pressure": value.queue_pressure,
            }
        if isinstance(value, AttackEvent):
            return {
                "event_id": value.event_id,
                "agent": value.agent,
                "selected_at": value.selected_at,
                "attack_type": value.candidate.attack_type,
                "target_link": value.candidate.target_link,
                "score": round(value.score, 6),
            }
        if isinstance(value, DefenseEvent):
            return {
                "event_id": value.event_id,
                "agent": value.agent,
                "time_sec": value.time_sec,
                "action": value.action,
                "details": to_plain_dict(value.details),
            }
        if isinstance(value, list):
            summarized = [self._summarize(item) for item in value[:8]]
            if len(value) > 8:
                summarized.append({"truncated_count": len(value) - 8})
            return summarized
        if isinstance(value, tuple):
            return self._summarize(list(value))
        if isinstance(value, dict):
            items = list(value.items())[:20]
            summarized = {str(key): self._summarize(item_value) for key, item_value in items}
            if len(value) > 20:
                summarized["truncated_count"] = len(value) - 20
            return summarized
        if isinstance(value, float):
            return round(value, 6)
        if isinstance(value, (str, int, bool)) or value is None:
            return value
        if hasattr(value, "__dataclass_fields__"):
            return self._summarize(to_plain_dict(value))
        return str(value)
