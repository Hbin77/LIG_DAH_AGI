from __future__ import annotations

from pathlib import Path

from src.agents.runtime import AgentRuntime
from src.agents.schema import AgentObservation, ToolCallRecord
from src.aura.candidate_generator import candidate_trace_payload, generate_candidates
from src.aura.impact_estimator import estimate_candidate_effect, estimate_detectability
from src.shared.metrics import compute_attack_score
from src.shared.schemas import AttackEvent, MissionState


class RuleAURA:
    def __init__(
        self,
        attack_threshold: float = 0.12,
        cooldown_sec: float = 45.0,
        max_events: int = 5,
        min_start_sec: float = 60.0,
    ) -> None:
        self.attack_threshold = attack_threshold
        self.cooldown_sec = cooldown_sec
        self.max_events = max_events
        self.min_start_sec = min_start_sec
        self.last_attack_time = -10_000.0
        self.event_count = 0
        self.runtime = AgentRuntime(
            agent_name="AURA",
            goal="maximize simulated mission impact while staying inside safety constraints",
        )
        self.runtime.register_tool(
            "generate_attack_candidates",
            "Generate safe simulated attack-effect candidates from mission state",
            generate_candidates,
        )
        self.runtime.register_tool(
            "estimate_candidate_effect",
            "Estimate candidate impact with analytic queue/link approximation",
            estimate_candidate_effect,
        )
        self.runtime.register_tool(
            "estimate_detectability",
            "Estimate how obvious the simulated attack effect is to the defender",
            estimate_detectability,
        )
        self.runtime.register_tool(
            "summarize_defense_context",
            "Summarize recent TSRA-R defense actions for AURA counter-defense context",
            self._summarize_defense_context,
        )

    def bind_runtime(self, trace_path: Path) -> None:
        self.runtime.bind_trace_log(trace_path)

    def decide(self, state: MissionState) -> AttackEvent | None:
        observation = self.runtime.observe(state)
        tool_calls: list[ToolCallRecord] = []
        candidate_actions: list[dict] = []
        defense_context = self.runtime.call_tool(
            "summarize_defense_context",
            tool_calls,
            state=state,
        )
        self._update_defense_context_belief(defense_context)

        if state.time_sec < self.min_start_sec:
            self._record_noop(
                state,
                observation,
                candidate_actions,
                tool_calls,
                f"waiting for min_start_sec={self.min_start_sec}",
                defense_context=defense_context,
            )
            return None
        if self.event_count >= self.max_events:
            self._record_noop(
                state,
                observation,
                candidate_actions,
                tool_calls,
                f"max_events={self.max_events} reached",
                defense_context=defense_context,
            )
            return None
        if state.time_sec - self.last_attack_time < self.cooldown_sec:
            self._record_noop(
                state,
                observation,
                candidate_actions,
                tool_calls,
                "attack cooldown active",
                {"cooldown_remaining_sec": self.cooldown_sec - (state.time_sec - self.last_attack_time)},
                defense_context=defense_context,
            )
            return None

        scored = []
        candidates = self.runtime.call_tool(
            "generate_attack_candidates",
            tool_calls,
            state=state,
        )
        for candidate in candidates:
            predicted = self.runtime.call_tool(
                "estimate_candidate_effect",
                tool_calls,
                state=state,
                candidate=candidate,
                horizon_sec=120,
            )
            impact = predicted["mission_impact"]
            detectability = self.runtime.call_tool(
                "estimate_detectability",
                tool_calls,
                candidate=candidate,
                predicted=predicted,
            )
            score = compute_attack_score(impact, detectability)
            scored.append((score, candidate, predicted, detectability))
            candidate_actions.append(
                {
                    **candidate_trace_payload(candidate),
                    "score": round(score, 6),
                    "predicted_mission_impact": round(impact, 6),
                    "detectability_score": round(detectability, 6),
                    "cross_agent_defense_context": defense_context,
                    "cross_agent_defense_context_used": self._defense_context_used(defense_context),
                }
            )

        if not scored:
            self._record_noop(
                state,
                observation,
                candidate_actions,
                tool_calls,
                "no candidate actions generated",
                defense_context=defense_context,
            )
            return None

        best_score, best_candidate, best_prediction, detectability = max(
            scored, key=lambda item: item[0]
        )
        if best_score < self.attack_threshold:
            self._record_noop(
                state,
                observation,
                candidate_actions,
                tool_calls,
                "best candidate below attack threshold",
                {
                    "best_score": best_score,
                    "attack_threshold": self.attack_threshold,
                    "best_attack_type": best_candidate.attack_type,
                },
                defense_context=defense_context,
            )
            return None

        self.last_attack_time = state.time_sec
        self.event_count += 1
        best_prediction["detectability_score"] = detectability
        event = AttackEvent(
            event_id=f"atk-{self.event_count:05d}",
            selected_at=state.time_sec,
            candidate=best_candidate,
            expected_impact=best_prediction,
            reason=best_candidate.reason,
            score=best_score,
        )
        self.runtime.memory.update_belief("last_attack_time", self.last_attack_time)
        self.runtime.memory.update_belief("event_count", self.event_count)
        self.runtime.memory.update_belief("last_attack_type", best_candidate.attack_type)
        self.runtime.record_decision(
            time_sec=state.time_sec,
            policy="rule_attack_score",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action={
                "type": "attack_event",
                "event_id": event.event_id,
                "attack_type": best_candidate.attack_type,
                "target_link": best_candidate.target_link,
                "score": round(best_score, 6),
            },
            reason=best_candidate.reason,
            feedback={
                "attack_threshold": self.attack_threshold,
                "cooldown_sec": self.cooldown_sec,
                "remaining_event_budget": self.max_events - self.event_count,
                "defense_context": defense_context,
            },
        )
        return event

    @staticmethod
    def _summarize_defense_context(state: MissionState) -> dict:
        active_actions = list(state.active_defense_actions)
        recent_actions = list(state.recent_defense_actions)
        return {
            "defense_mode": state.defense_mode,
            "active_defense_actions": active_actions,
            "recent_defense_actions": recent_actions,
            "last_defense_time_sec": state.last_defense_time_sec,
            "last_defense_action": state.last_defense_action,
            "active_defense_count": len(active_actions),
            "recent_defense_count": len(recent_actions),
            "counter_defense_context_seen": bool(
                active_actions or recent_actions or state.defense_mode != "none"
            ),
        }

    def _update_defense_context_belief(self, defense_context: dict) -> None:
        self.runtime.memory.update_belief("defense_context", defense_context)
        self.runtime.memory.update_belief(
            "counter_defense_context_seen",
            bool(defense_context.get("counter_defense_context_seen")),
        )

    @staticmethod
    def _defense_context_used(defense_context: dict) -> bool:
        return bool(defense_context.get("counter_defense_context_seen"))

    def _record_noop(
        self,
        state: MissionState,
        observation: AgentObservation,
        candidate_actions: list[dict],
        tool_calls: list[ToolCallRecord],
        reason: str,
        feedback: dict | None = None,
        defense_context: dict | None = None,
    ) -> None:
        feedback_payload = feedback or {
            "attack_threshold": self.attack_threshold,
            "cooldown_sec": self.cooldown_sec,
            "event_count": self.event_count,
        }
        if defense_context is not None:
            feedback_payload = dict(feedback_payload)
            feedback_payload["defense_context"] = defense_context
        self.runtime.record_decision(
            time_sec=state.time_sec,
            policy="rule_attack_score",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action={"type": "no_op"},
            reason=reason,
            feedback=feedback_payload,
        )
