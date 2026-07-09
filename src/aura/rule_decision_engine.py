from __future__ import annotations

from pathlib import Path

from src.agents.runtime import AgentRuntime
from src.agents.schema import AgentObservation, ToolCallRecord
from src.aura.candidate_generator import generate_candidates
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

    def bind_runtime(self, trace_path: Path) -> None:
        self.runtime.bind_trace_log(trace_path)

    def decide(self, state: MissionState) -> AttackEvent | None:
        observation = self.runtime.observe(state)
        tool_calls: list[ToolCallRecord] = []
        candidate_actions: list[dict] = []

        if state.time_sec < self.min_start_sec:
            self._record_noop(
                state,
                observation,
                candidate_actions,
                tool_calls,
                f"waiting for min_start_sec={self.min_start_sec}",
            )
            return None
        if self.event_count >= self.max_events:
            self._record_noop(
                state,
                observation,
                candidate_actions,
                tool_calls,
                f"max_events={self.max_events} reached",
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
                    "action": candidate.attack_type,
                    "target_link": candidate.target_link,
                    "score": round(score, 6),
                    "predicted_mission_impact": round(impact, 6),
                    "detectability_score": round(detectability, 6),
                    "reason": candidate.reason,
                }
            )

        if not scored:
            self._record_noop(
                state,
                observation,
                candidate_actions,
                tool_calls,
                "no candidate actions generated",
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
            },
        )
        return event

    def _record_noop(
        self,
        state: MissionState,
        observation: AgentObservation,
        candidate_actions: list[dict],
        tool_calls: list[ToolCallRecord],
        reason: str,
        feedback: dict | None = None,
    ) -> None:
        self.runtime.record_decision(
            time_sec=state.time_sec,
            policy="rule_attack_score",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action={"type": "no_op"},
            reason=reason,
            feedback=feedback
            or {
                "attack_threshold": self.attack_threshold,
                "cooldown_sec": self.cooldown_sec,
                "event_count": self.event_count,
            },
        )
