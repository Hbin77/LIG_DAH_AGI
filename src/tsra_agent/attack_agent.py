from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from .agents import AURALite, MissionState
from .attack_ml_policy import (
    ATTACK_FEATURE_NAMES,
    AttackImpactModel,
    attack_candidate_features,
    attack_model_backend_name,
    load_attack_model,
    load_attack_policy_config,
    validate_attack_ml_scope,
)
from .models import AttackAction, AttackMode, LinkName
from .runtime import AgentRuntime, closed_synthetic_tool_validator


DEFAULT_ATTACK_POLICY_CONFIG = {
    "detectability_weight": 0.05,
    "repeated_tactic_penalty": 0.03,
    "minimum_predicted_impact": 0.02,
    "commitment_ticks": 4.0,
}


@dataclass(frozen=True)
class AttackSelection:
    action: AttackAction
    selected_candidate: dict[str, Any]
    candidate_count: int


class AURAAgent:
    """Attack-side agent with independent runtime, memory, tools, and traces."""

    def __init__(
        self,
        scenario: AttackMode,
        *,
        policy_kind: str = "rule",
        impact_model: AttackImpactModel | None = None,
        policy_config: dict[str, float] | None = None,
        retain_traces: bool = True,
        episode_ticks: int | None = None,
    ) -> None:
        if policy_kind not in {"rule", "ml"}:
            raise ValueError(f"unsupported AURA policy kind: {policy_kind}")
        if policy_kind == "ml":
            validate_attack_ml_scope(scenario, episode_ticks or -1)
        self.policy = AURALite(scenario)
        self.policy_kind = policy_kind
        self.impact_model = (
            impact_model or load_attack_model()
            if policy_kind == "ml"
            else None
        )
        self.model_backend = (
            attack_model_backend_name(self.impact_model)
            if self.impact_model is not None
            else "rule_candidate_ranker"
        )
        loaded_config = load_attack_policy_config() if policy_kind == "ml" else {}
        self.policy_config = {
            **DEFAULT_ATTACK_POLICY_CONFIG,
            **loaded_config,
            **(policy_config or {}),
        }
        self.action_counts: Counter[str] = Counter()
        self.selection_source_counts: Counter[str] = Counter()
        self.model_influenced_ticks = 0
        self.model_changed_rule_ticks = 0
        self.model_inference_ticks = 0
        agent_name = "AURA-ML" if policy_kind == "ml" else "AURA-lite"
        self.runtime = AgentRuntime(
            agent_name=agent_name,
            goal="select bounded simulated mission-effect attacks",
            retain_traces=retain_traces,
        )
        self.runtime.register_tool(
            "generate_attack_candidates",
            "generate bounded synthetic attack-effect candidates from mission state",
            self._generate_attack_candidates,
            input_summarizer=self._generate_input_summary,
            output_summarizer=lambda candidates: {
                "candidate_count": len(candidates),
                "eligible_count": sum(1 for row in candidates if row["eligible"]),
                "actions": [row["action"] for row in candidates],
            },
            safety_validator=closed_synthetic_tool_validator,
            allowed_input_fields={"state"},
        )
        if self.impact_model is not None:
            self.runtime.register_tool(
                "predict_attack_impacts",
                "predict counterfactual simulator impact for each synthetic candidate",
                self._predict_attack_impacts,
                input_summarizer=self._prediction_input_summary,
                output_summarizer=lambda predictions: {
                    "prediction_count": len(predictions),
                    "minimum": round(min(predictions), 6) if predictions else None,
                    "maximum": round(max(predictions), 6) if predictions else None,
                    "model_backend": self.model_backend,
                    "feature_count": len(ATTACK_FEATURE_NAMES),
                },
                safety_validator=closed_synthetic_tool_validator,
                allowed_input_fields={"state", "candidates"},
            )
        self.runtime.register_tool(
            "rank_attack_candidates",
            "rank candidates using rule or learned rollout impact and bounded guardrails",
            self._rank_attack_candidates,
            input_summarizer=self._rank_input_summary,
            output_summarizer=self._rank_output_summary,
            safety_validator=closed_synthetic_tool_validator,
            allowed_input_fields={
                "state",
                "candidates",
                "predictions",
                "memory_context",
                "forced_mode",
                "override_source",
            },
        )
        self.runtime.register_tool(
            "select_attack_effect",
            "materialize the highest-ranked safe candidate as a synthetic attack action",
            self._select_attack_effect,
            input_summarizer=lambda kwargs: {
                "candidate_count": len(kwargs["candidates"]),
                "eligible_actions": [
                    row["action"] for row in kwargs["candidates"] if row["eligible"]
                ],
            },
            output_summarizer=self._selection_summary,
            safety_validator=closed_synthetic_tool_validator,
            allowed_input_fields={"candidates"},
        )

    @property
    def attack_start(self) -> int:
        return self.policy.attack_start

    @property
    def max_pulses(self) -> int:
        return self.policy.max_pulses

    def decide(
        self,
        state: MissionState,
        *,
        forced_mode: AttackMode | None = None,
    ) -> AttackAction:
        self.runtime.begin_cycle(state)
        memory_context = self.runtime.memory.summary()
        external_forced_mode = forced_mode
        commitment_remaining = int(
            memory_context.get("belief_state", {}).get("commitment_remaining", 0)
        )
        commitment_mode = None
        if (
            external_forced_mode is None
            and self.policy_kind == "ml"
            and commitment_remaining > 0
        ):
            commitment_mode = AttackMode(
                memory_context["belief_state"]["committed_attack_mode"]
            )
        effective_forced_mode = external_forced_mode or commitment_mode
        override_source = (
            "counterfactual_rollout_override"
            if external_forced_mode is not None
            else "memory_commitment"
            if commitment_mode is not None
            else None
        )
        raw_candidates = self.runtime.call_tool(
            "generate_attack_candidates",
            state=state,
        )
        predictions = None
        model_inference_executed = bool(
            self.impact_model is not None
            and effective_forced_mode is None
            and any(
                candidate["eligible"]
                and candidate["action"] != AttackMode.NONE.value
                for candidate in raw_candidates
            )
        )
        if model_inference_executed:
            predictions = self.runtime.call_tool(
                "predict_attack_impacts",
                state=state,
                candidates=raw_candidates,
            )
            self.model_inference_ticks += 1
        candidates = self.runtime.call_tool(
            "rank_attack_candidates",
            state=state,
            candidates=raw_candidates,
            predictions=predictions,
            memory_context=memory_context,
            forced_mode=effective_forced_mode,
            override_source=override_source,
        )
        selection: AttackSelection = self.runtime.call_tool(
            "select_attack_effect",
            candidates=candidates,
        )
        action = selection.action
        selected = selection.selected_candidate

        if self.policy_kind == "ml" and external_forced_mode is None:
            if commitment_mode is not None and action.mode != AttackMode.NONE:
                next_remaining = max(0, commitment_remaining - 1)
            elif action.mode != AttackMode.NONE:
                next_remaining = max(
                    0,
                    int(self.policy_config["commitment_ticks"]) - 1,
                )
            else:
                next_remaining = 0
            self.runtime.memory.update_belief(
                "committed_attack_mode",
                action.mode.value if next_remaining else AttackMode.NONE.value,
            )
            self.runtime.memory.update_belief(
                "commitment_remaining",
                next_remaining,
            )

        self.runtime.memory.update_belief("last_attack_mode", action.mode.value)
        self.runtime.memory.update_belief("last_target_link", action.target_link.value)
        self.runtime.memory.update_belief("last_attack_score", selected["score"])
        self.runtime.memory.update_belief(
            "active_attack_tick_count",
            int(self.runtime.memory.belief_state.get("active_attack_tick_count", 0))
            + int(action.mode != AttackMode.NONE),
        )
        decision_basis = {
            "policy_kind": self.policy_kind,
            "model_backend": self.model_backend,
            "predicted_incremental_impact": selected.get("predicted_incremental_impact"),
            "detectability_score": selected.get("detectability_score", 0.0),
            "rule_selected_action": selected["rule_selected_action"],
            "zero_model_selected_action": selected["zero_model_selected_action"],
            "model_influenced": bool(selected.get("model_influenced", False)),
            "model_changed_rule_choice": bool(selected.get("model_changed_rule_choice", False)),
            "model_inference_executed": model_inference_executed,
            "selection_source": selected["selection_source"],
            "commitment_ticks": (
                int(self.policy_config["commitment_ticks"])
                if self.policy_kind == "ml"
                else 1
            ),
        }
        self.action_counts[action.mode.value] += 1
        self.selection_source_counts[selected["selection_source"]] += 1
        self.model_influenced_ticks += int(decision_basis["model_influenced"])
        self.model_changed_rule_ticks += int(
            decision_basis["model_changed_rule_choice"]
        )
        self.runtime.commit_decision(
            tick=state.tick,
            policy=(
                "aura_counterfactual_rollout_override"
                if external_forced_mode is not None
                else "aura_ml_rollout_impact"
                if self.policy_kind == "ml"
                else "aura_lite_candidate_ranker"
            ),
            candidate_actions=candidates,
            selected_action={
                "type": "attack_action" if action.mode != AttackMode.NONE else "no_op",
                "mode": action.mode.value,
                "target_link": action.target_link.value,
                "intensity": round(action.intensity, 4),
                "score": selected["score"],
                "predicted_effect": selected["predicted_effect"],
                "decision_basis": decision_basis,
            },
            reason=action.rationale,
            feedback={
                "closed_simulation_only": True,
                "attack_start": self.policy.attack_start,
                "max_pulses": self.policy.max_pulses,
                "counterfactual_override": (
                    external_forced_mode.value if external_forced_mode else None
                ),
                "memory_commitment": commitment_mode.value if commitment_mode else None,
            },
        )
        return action

    def attach_feedback(self, feedback: dict[str, Any]) -> None:
        self.runtime.attach_feedback(feedback)

    def _generate_attack_candidates(self, *, state: MissionState) -> list[dict[str, Any]]:
        return self.policy.rank_candidates(state)

    def _predict_attack_impacts(
        self,
        *,
        state: MissionState,
        candidates: list[dict[str, Any]],
    ) -> list[float]:
        if self.impact_model is None:
            raise RuntimeError("attack impact model is not configured")
        rows = [attack_candidate_features(state, candidate) for candidate in candidates]
        return [float(value) for value in self.impact_model.predict(rows)]

    def _rank_attack_candidates(
        self,
        *,
        state: MissionState,
        candidates: list[dict[str, Any]],
        predictions: list[float] | None,
        memory_context: dict[str, Any],
        forced_mode: AttackMode | None,
        override_source: str | None,
    ) -> list[dict[str, Any]]:
        if predictions is not None and len(predictions) != len(candidates):
            raise ValueError("one learned prediction is required per attack candidate")

        ranked: list[dict[str, Any]] = []
        last_mode = memory_context.get("belief_state", {}).get("last_attack_mode")
        for index, raw_candidate in enumerate(candidates):
            candidate = {
                **raw_candidate,
                "predicted_effect": dict(raw_candidate["predicted_effect"]),
            }
            candidate["rule_score"] = float(raw_candidate["score"])
            candidate["memory_adjustment"] = 0.0
            if (
                candidate["eligible"]
                and candidate["action"] != AttackMode.NONE.value
                and candidate["action"] == last_mode
            ):
                candidate["memory_adjustment"] = -0.01

            candidate["predicted_incremental_impact"] = (
                round(float(predictions[index]), 6)
                if predictions is not None
                else None
            )
            candidate["detectability_score"] = round(
                self._estimate_detectability(state, candidate),
                6,
            )
            if predictions is None:
                score = candidate["rule_score"] + candidate["memory_adjustment"]
                candidate["selection_source"] = "rule_score"
            elif candidate["action"] == AttackMode.NONE.value:
                score = 0.0
                candidate["selection_source"] = "learned_rollout_impact"
            elif not candidate["eligible"]:
                score = -1_000_000.0
                candidate["selection_source"] = "ineligible"
            else:
                prediction = float(predictions[index])
                minimum = self.policy_config["minimum_predicted_impact"]
                below_minimum_penalty = max(0.0, minimum - prediction)
                repeated_penalty = (
                    self.policy_config["repeated_tactic_penalty"]
                    if candidate["action"] == last_mode
                    else 0.0
                )
                score = (
                    prediction
                    - self.policy_config["detectability_weight"]
                    * candidate["detectability_score"]
                    - repeated_penalty
                    - below_minimum_penalty
                )
                candidate["selection_source"] = "learned_rollout_impact"
            candidate["score"] = round(float(score), 6)
            candidate["selected"] = False
            ranked.append(candidate)

        rule_choice = max(
            ranked,
            key=lambda row: row["rule_score"] + row["memory_adjustment"],
        )["action"]
        zero_model_choice = max(
            ranked,
            key=self._zero_model_score,
        )["action"]
        selected = max(ranked, key=lambda row: row["score"])
        if forced_mode is not None:
            forced = next(
                (
                    row
                    for row in ranked
                    if row["action"] == forced_mode.value and row["eligible"]
                ),
                next(row for row in ranked if row["action"] == AttackMode.NONE.value),
            )
            forced["unforced_score"] = forced["score"]
            forced["score"] = round(max(row["score"] for row in ranked) + 1.0, 6)
            forced["selection_source"] = override_source or "policy_override"
            selected = forced

        for candidate in ranked:
            candidate["selected"] = candidate is selected
            candidate["rule_selected_action"] = rule_choice
            candidate["zero_model_selected_action"] = zero_model_choice
            candidate["model_influenced"] = (
                predictions is not None
                and candidate is selected
                and selected["action"] != zero_model_choice
            )
            candidate["model_changed_rule_choice"] = (
                predictions is not None
                and candidate is selected
                and selected["action"] != rule_choice
            )
        return ranked

    def _zero_model_score(self, candidate: dict[str, Any]) -> float:
        if candidate["action"] == AttackMode.NONE.value:
            return 0.0
        if not candidate["eligible"]:
            return -1_000_000.0
        return -self.policy_config["detectability_weight"] * float(
            candidate["detectability_score"]
        )

    @staticmethod
    def _estimate_detectability(
        state: MissionState,
        candidate: dict[str, Any],
    ) -> float:
        if candidate["action"] == AttackMode.NONE.value:
            return 0.0
        score = 0.45 * float(candidate["intensity"])
        if candidate["target_link"] == state.active_link.value:
            score += 0.10
        if candidate["action"] == AttackMode.FAILOVER_CHASING.value:
            score += 0.08
        return min(1.0, score)

    @staticmethod
    def _select_attack_effect(*, candidates: list[dict[str, Any]]) -> AttackSelection:
        selected = next(row for row in candidates if row["selected"])
        action = AttackAction(
            mode=AttackMode(selected["action"]),
            target_link=LinkName(selected["target_link"]),
            intensity=float(selected["intensity"]),
            duration=int(selected["duration"]),
            rationale=str(selected["reason"]),
        )
        return AttackSelection(
            action=action,
            selected_candidate=selected,
            candidate_count=len(candidates),
        )

    @staticmethod
    def _generate_input_summary(kwargs: dict[str, Any]) -> dict[str, Any]:
        state: MissionState = kwargs["state"]
        return {
            "tick": state.tick,
            "scenario": state.current_attack.value,
            "active_link": state.active_link.value,
            "queue_depth": state.queue_depth,
            "critical_queue_depth": state.critical_queue_depth,
        }

    def _prediction_input_summary(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        state: MissionState = kwargs["state"]
        return {
            "tick": state.tick,
            "candidate_count": len(kwargs["candidates"]),
            "model_backend": self.model_backend,
            "feature_count": len(attack_candidate_features(state, kwargs["candidates"][0])),
        }

    @staticmethod
    def _rank_input_summary(kwargs: dict[str, Any]) -> dict[str, Any]:
        state: MissionState = kwargs["state"]
        memory_context = kwargs["memory_context"]
        return {
            "tick": state.tick,
            "candidate_count": len(kwargs["candidates"]),
            "prediction_count": len(kwargs["predictions"] or []),
            "last_attack_mode": memory_context.get("belief_state", {}).get("last_attack_mode"),
            "previous_decision_count": memory_context.get("recent_decision_count", 0),
            "forced_mode": kwargs["forced_mode"].value if kwargs["forced_mode"] else None,
            "override_source": kwargs["override_source"],
        }

    @staticmethod
    def _rank_output_summary(candidates: list[dict[str, Any]]) -> dict[str, Any]:
        selected = next(row for row in candidates if row["selected"])
        return {
            "candidate_count": len(candidates),
            "eligible_count": sum(1 for row in candidates if row["eligible"]),
            "selected_action": selected["action"],
            "selected_score": selected["score"],
            "selection_source": selected["selection_source"],
            "model_influenced": selected["model_influenced"],
        }

    @staticmethod
    def _selection_summary(selection: AttackSelection) -> dict[str, Any]:
        return {
            "mode": selection.action.mode.value,
            "target_link": selection.action.target_link.value,
            "intensity": round(selection.action.intensity, 4),
            "selected_score": selection.selected_candidate["score"],
            "candidate_count": selection.candidate_count,
        }
