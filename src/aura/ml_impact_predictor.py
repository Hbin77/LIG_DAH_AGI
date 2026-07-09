from __future__ import annotations

import pickle
from pathlib import Path

from src.agents.runtime import AgentRuntime
from src.agents.schema import AgentObservation, ToolCallRecord
from src.aura.candidate_generator import candidate_trace_payload, generate_candidates
from src.aura.impact_estimator import estimate_candidate_effect, estimate_detectability
from src.aura.rule_decision_engine import RuleAURA
from src.shared.features import candidate_features
from src.shared.metrics import compute_attack_score
from src.shared.schemas import AttackEvent, MissionState


class MLAURA:
    def __init__(
        self,
        model_path: Path = Path("outputs/models/aura_impact_model.pkl"),
        attack_threshold: float = 0.12,
        cooldown_sec: float = 45.0,
        max_events: int = 5,
        min_start_sec: float = 60.0,
        stale_cop_objective_bonus: float = 0.20,
        counter_defense_bonus: float = 0.08,
        repeated_tactic_penalty: float = 0.04,
    ) -> None:
        self.attack_threshold = attack_threshold
        self.cooldown_sec = cooldown_sec
        self.max_events = max_events
        self.min_start_sec = min_start_sec
        self.stale_cop_objective_bonus = stale_cop_objective_bonus
        self.counter_defense_bonus = counter_defense_bonus
        self.repeated_tactic_penalty = repeated_tactic_penalty
        self.last_attack_time = -10_000.0
        self.event_count = 0
        self.attack_type_counts: dict[str, int] = {}
        if not model_path.exists():
            self.model = None
            self.fallback = RuleAURA(attack_threshold, cooldown_sec, max_events, min_start_sec)
        else:
            with model_path.open("rb") as f:
                self.model = pickle.load(f)
            self.fallback = None
        self.runtime = AgentRuntime(
            agent_name="AURA-ML",
            goal="select simulated attack effect using learned mission-impact prediction",
        )
        self.runtime.register_tool(
            "generate_attack_candidates",
            "Generate safe simulated attack-effect candidates from mission state",
            generate_candidates,
        )
        self.runtime.register_tool(
            "predict_candidate_impact",
            "Predict candidate mission impact using the trained AURA model",
            self._predict_candidate_impact,
        )
        self.runtime.register_tool(
            "estimate_candidate_effect",
            "Estimate non-target metrics with analytic queue/link approximation",
            estimate_candidate_effect,
        )
        self.runtime.register_tool(
            "estimate_detectability",
            "Estimate how obvious the simulated attack effect is to the defender",
            estimate_detectability,
        )
        self.runtime.register_tool(
            "summarize_defense_context",
            "Summarize recent TSRA-R defense actions for AURA-ML counter-defense context",
            self._summarize_defense_context,
        )

    def bind_runtime(self, trace_path: Path) -> None:
        self.runtime.bind_trace_log(trace_path)
        if self.fallback:
            self.fallback.bind_runtime(trace_path)

    def decide(self, state: MissionState) -> AttackEvent | None:
        if self.model is None:
            return self.fallback.decide(state) if self.fallback else None

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
            predicted_impact = self.runtime.call_tool(
                "predict_candidate_impact",
                tool_calls,
                state=state,
                candidate=candidate,
            )
            predicted = self.runtime.call_tool(
                "estimate_candidate_effect",
                tool_calls,
                state=state,
                candidate=candidate,
                horizon_sec=120,
            )
            detectability = self.runtime.call_tool(
                "estimate_detectability",
                tool_calls,
                candidate=candidate,
                predicted=predicted,
            )
            base_score = compute_attack_score(predicted_impact, detectability)
            objective_bonus, repeated_penalty, objective_reason = self._objective_adjustment(
                state=state,
                attack_type=candidate.attack_type,
            )
            counter_bonus, counter_reason = self._counter_defense_adjustment(
                state=state,
                attack_type=candidate.attack_type,
                defense_context=defense_context,
            )
            score = base_score + objective_bonus + counter_bonus - repeated_penalty
            predicted["mission_impact"] = predicted_impact
            predicted["detectability_score"] = detectability
            predicted["base_attack_score"] = base_score
            predicted["objective_bonus"] = objective_bonus
            predicted["counter_defense_bonus"] = counter_bonus
            predicted["repeated_tactic_penalty"] = repeated_penalty
            predicted["selection_score"] = score
            predicted["objective_reason"] = objective_reason
            predicted["counter_defense_reason"] = counter_reason
            scored.append((score, candidate, predicted))
            candidate_actions.append(
                {
                    **candidate_trace_payload(candidate),
                    "score": round(score, 6),
                    "base_attack_score": round(base_score, 6),
                    "objective_bonus": round(objective_bonus, 6),
                    "counter_defense_bonus": round(counter_bonus, 6),
                    "repeated_tactic_penalty": round(repeated_penalty, 6),
                    "selection_score": round(score, 6),
                    "predicted_mission_impact": round(predicted_impact, 6),
                    "detectability_score": round(detectability, 6),
                    "objective_reason": objective_reason,
                    "counter_defense_reason": counter_reason,
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

        best_score, best_candidate, best_prediction = max(scored, key=lambda item: item[0])
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
        self.attack_type_counts[best_candidate.attack_type] = (
            self.attack_type_counts.get(best_candidate.attack_type, 0) + 1
        )
        event = AttackEvent(
            event_id=f"ml-atk-{self.event_count:05d}",
            selected_at=state.time_sec,
            candidate=best_candidate,
            expected_impact=best_prediction,
            reason=f"ML impact predictor selected {best_candidate.attack_type}",
            score=best_score,
            agent="AURA-ML",
        )
        self.runtime.memory.update_belief("last_attack_time", self.last_attack_time)
        self.runtime.memory.update_belief("event_count", self.event_count)
        self.runtime.memory.update_belief("last_attack_type", best_candidate.attack_type)
        self.runtime.memory.update_belief("attack_type_counts", dict(self.attack_type_counts))
        self.runtime.memory.update_belief(
            "last_objective_bonus",
            best_prediction.get("objective_bonus", 0.0),
        )
        self.runtime.record_decision(
            time_sec=state.time_sec,
            policy="ml_impact_predictor",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action={
                "type": "attack_event",
                "event_id": event.event_id,
                "attack_type": best_candidate.attack_type,
                "target_link": best_candidate.target_link,
                "score": round(best_score, 6),
                "base_attack_score": round(best_prediction.get("base_attack_score", best_score), 6),
                "objective_bonus": round(best_prediction.get("objective_bonus", 0.0), 6),
                "counter_defense_bonus": round(best_prediction.get("counter_defense_bonus", 0.0), 6),
                "repeated_tactic_penalty": round(
                    best_prediction.get("repeated_tactic_penalty", 0.0),
                    6,
                ),
                "objective_reason": best_prediction.get("objective_reason", "base_score"),
                "counter_defense_reason": best_prediction.get("counter_defense_reason", "no_counter_defense_adjustment"),
            },
            reason=f"ML impact predictor selected {best_candidate.attack_type}",
            feedback={
                "attack_threshold": self.attack_threshold,
                "cooldown_sec": self.cooldown_sec,
                "remaining_event_budget": self.max_events - self.event_count,
                "attack_type_counts": dict(self.attack_type_counts),
                "selected_base_attack_score": round(best_prediction.get("base_attack_score", best_score), 6),
                "selected_objective_bonus": round(best_prediction.get("objective_bonus", 0.0), 6),
                "selected_counter_defense_bonus": round(best_prediction.get("counter_defense_bonus", 0.0), 6),
                "selected_repeated_tactic_penalty": round(
                    best_prediction.get("repeated_tactic_penalty", 0.0),
                    6,
                ),
                "defense_context": defense_context,
            },
        )
        return event

    def _objective_adjustment(
        self,
        *,
        state: MissionState,
        attack_type: str,
    ) -> tuple[float, float, str]:
        objective_bonus = 0.0
        repeated_penalty = 0.0
        reasons: list[str] = []
        prior_count = self.attack_type_counts.get(attack_type, 0)
        if prior_count:
            repeated_penalty = min(self.repeated_tactic_penalty * prior_count, 0.12)
            reasons.append(f"repeat_penalty_count={prior_count}")
        if (
            attack_type == "stale_cop_induction"
            and self.event_count >= self.max_events - 1
            and prior_count == 0
            and state.stale_data_ratio > 0.20
        ):
            objective_bonus = self.stale_cop_objective_bonus
            reasons.append("uncovered_stale_cop_objective")
        return objective_bonus, repeated_penalty, "+".join(reasons) if reasons else "base_score"

    def _counter_defense_adjustment(
        self,
        *,
        state: MissionState,
        attack_type: str,
        defense_context: dict,
    ) -> tuple[float, str]:
        active_actions = set(defense_context.get("active_defense_actions") or [])
        recent_actions = set(defense_context.get("recent_defense_actions") or [])
        actions = active_actions | recent_actions
        defense_mode = str(defense_context.get("defense_mode") or state.defense_mode)

        if not defense_context.get("counter_defense_context_seen"):
            return 0.0, "no_counter_defense_context"
        if (
            attack_type == "failover_chasing"
            and state.active_link != "SATCOM"
            and ("pace_switch" in actions or defense_mode == "pace_switch")
        ):
            return self.counter_defense_bonus, "counter_pace_failover_chasing"
        if (
            attack_type == "queue_pressure"
            and actions.intersection({"priority_reroute", "video_throttle"})
            and state.video_queue_kb > 500.0
        ):
            return min(self.counter_defense_bonus * 0.5, 0.04), "counter_priority_video_pressure"
        return 0.0, "defense_context_observed_no_score_change"

    def _predict_candidate_impact(self, state: MissionState, candidate) -> float:
        features = candidate_features(state, candidate)
        return float(self.model.predict([features])[0])

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
            policy="ml_impact_predictor",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action={"type": "no_op"},
            reason=reason,
            feedback=feedback_payload,
        )
