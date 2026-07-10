from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agents import MissionState, MLTSRARLite, TSRARLite
from .models import DefenseAction, LinkName
from .ml_policy import sklearn_backend_name
from .runtime import AgentRuntime, closed_synthetic_tool_validator


@dataclass(frozen=True)
class RiskPrediction:
    probability: float
    model_backend: str
    feature_count: int


@dataclass
class ThresholdRulePolicy(TSRARLite):
    """Deliberately simple comparator kept outside the adaptive TSRA-R policy."""

    def assess_state(self, state: MissionState) -> dict[str, Any]:
        degraded = state.satcom_health < 0.45
        critical_delay = state.critical_latency_window > 10.0
        stale_pressure = state.stale_ratio_window > 0.35
        risk_score = min(
            1.0,
            0.55 * max(0.0, 1.0 - state.satcom_health)
            + 0.25 * min(1.0, state.critical_latency_window / 14.0)
            + 0.20 * min(1.0, state.stale_ratio_window / 0.45),
        )
        return {
            "policy_kind": "threshold_rule",
            "heuristic_risk": round(risk_score, 4),
            "fused_risk": round(risk_score, 4),
            "degraded": degraded,
            "critical_delay": critical_delay,
            "stale_pressure": stale_pressure,
            "traffic_manipulation": False,
            "access_pressure": False,
        }

    def choose_action(
        self,
        state: MissionState,
        assessment: dict[str, Any] | None = None,
    ) -> DefenseAction:
        assessment = assessment or self.assess_state(state)
        degraded = bool(assessment["degraded"])
        critical_delay = bool(assessment["critical_delay"])
        stale_pressure = bool(assessment["stale_pressure"])

        alert = None
        if degraded or critical_delay:
            if self.alert_tick is None:
                self.alert_tick = state.tick
            alert = (
                "rule alert: link degradation"
                if degraded
                else "rule alert: critical latency"
            )

        active_link = state.active_link
        if degraded and state.radio_health > 0.70:
            active_link = LinkName.RADIO

        if self.alert_tick is not None and self.recovery_tick is None:
            recovered = not degraded and not critical_delay and state.queue_depth < 8
            if recovered:
                self.stable_ticks += 1
                if self.stable_ticks >= 5:
                    self.recovery_tick = state.tick
            else:
                self.stable_ticks = 0

        priority_boost = degraded or critical_delay
        minimum_mode = degraded and (critical_delay or stale_pressure)
        pace_transition = active_link != state.active_link
        selected_actions = []
        if priority_boost:
            selected_actions.append("priority_boost")
        if minimum_mode:
            selected_actions.append("minimum_mode")
        if stale_pressure:
            selected_actions.append("stale_badge")
        if pace_transition:
            selected_actions.append("pace_transition")

        basis = {
            **assessment,
            "selected_actions": selected_actions,
            "action_triggers": {
                "priority_boost": (
                    (["link_degradation_threshold"] if degraded else [])
                    + (["critical_latency_threshold"] if critical_delay else [])
                ),
                "minimum_mode": (
                    ["compound_threshold"] if minimum_mode else []
                ),
                "stale_badge": (["stale_threshold"] if stale_pressure else []),
                "pace_transition": (
                    ["radio_fallback_threshold"] if pace_transition else []
                ),
                "quarantine": [],
            },
            "model_influenced_actions": [],
            "guardrail_triggered_actions": selected_actions,
        }
        return DefenseAction(
            active_link=active_link,
            priority_boost=priority_boost,
            minimum_mode=minimum_mode,
            alert=alert,
            stale_badge=stale_pressure,
            risk_score=float(assessment["fused_risk"]),
            quarantine=False,
            pace_transition=pace_transition,
            decision_basis=basis,
        )


class TSRAAgent:
    """Defense-side agent that executes rule, adaptive, or ML policy tools."""

    def __init__(
        self,
        mode: str,
        *,
        policy_config: dict[str, float] | None = None,
        sklearn_model: object | None = None,
        retain_traces: bool = True,
    ) -> None:
        if mode not in {"rule", "tsra", "ml"}:
            raise ValueError(f"unsupported defense agent mode: {mode}")
        self.mode = mode
        if mode == "rule":
            self.policy: TSRARLite = ThresholdRulePolicy()
            agent_name = "Rule-Defense"
        elif mode == "ml":
            kwargs: dict[str, Any] = {}
            if policy_config is not None:
                kwargs["policy_config"] = policy_config
            if sklearn_model is not None:
                kwargs["sklearn_model"] = sklearn_model
            self.policy = MLTSRARLite(**kwargs)
            agent_name = "TSRA-ML"
        else:
            self.policy = TSRARLite()
            agent_name = "TSRA-R-lite"

        self.runtime = AgentRuntime(
            agent_name=agent_name,
            goal="detect and mitigate synthetic C4ISR data-trust degradation",
            retain_traces=retain_traces,
        )
        if mode == "ml":
            self.runtime.register_tool(
                "extract_mission_features",
                "convert the current mission state into the trained detector feature contract",
                self._extract_mission_features,
                input_summarizer=self._state_input_summary,
                output_summarizer=lambda features: {
                    "feature_count": len(features),
                    "feature_vector": [round(value, 4) for value in features],
                },
                safety_validator=closed_synthetic_tool_validator,
                allowed_input_fields={"state"},
            )
            self.runtime.register_tool(
                "predict_mission_risk",
                "run the bundled trained model on the current synthetic mission features",
                self._predict_mission_risk,
                input_summarizer=lambda kwargs: {
                    "feature_count": len(kwargs["features"]),
                    "model_backend": self._model_backend(),
                },
                output_summarizer=lambda prediction: {
                    "ml_risk": round(prediction.probability, 4),
                    "model_backend": prediction.model_backend,
                    "feature_count": prediction.feature_count,
                },
                safety_validator=closed_synthetic_tool_validator,
                allowed_input_fields={"features"},
            )

        self.runtime.register_tool(
            "fuse_mission_risk",
            "combine model output and bounded mission safety signals into a risk basis",
            self._assess_mission_risk,
            input_summarizer=self._risk_input_summary,
            output_summarizer=lambda assessment: assessment,
            safety_validator=closed_synthetic_tool_validator,
            allowed_input_fields={"state", "prediction"},
        )
        self.runtime.register_tool(
            "select_defense_action",
            "select PACE, priority, freshness, load, and trust controls from the risk basis",
            self._select_defense_action,
            input_summarizer=lambda kwargs: {
                "tick": kwargs["state"].tick,
                "policy_kind": kwargs["assessment"]["policy_kind"],
                "fused_risk": kwargs["assessment"]["fused_risk"],
            },
            output_summarizer=self._defense_output_summary,
            safety_validator=closed_synthetic_tool_validator,
            allowed_input_fields={"state", "assessment"},
        )

    @property
    def alert_tick(self) -> int | None:
        return self.policy.alert_tick

    @property
    def recovery_tick(self) -> int | None:
        return self.policy.recovery_tick

    def decide(self, state: MissionState) -> DefenseAction:
        self.runtime.begin_cycle(state)
        prediction = None
        if self.mode == "ml":
            features = self.runtime.call_tool("extract_mission_features", state=state)
            prediction = self.runtime.call_tool(
                "predict_mission_risk",
                features=features,
            )
        assessment = self.runtime.call_tool(
            "fuse_mission_risk",
            state=state,
            prediction=prediction,
        )
        defense: DefenseAction = self.runtime.call_tool(
            "select_defense_action",
            state=state,
            assessment=assessment,
        )
        candidates = self._candidate_actions(defense)
        selected_flags = [
            candidate["action"]
            for candidate in candidates
            if candidate["selected"]
        ]

        self.runtime.memory.update_belief("last_risk_score", defense.risk_score)
        self.runtime.memory.update_belief("last_active_link", defense.active_link.value)
        self.runtime.memory.update_belief("last_decision_basis", defense.decision_basis)
        self.runtime.commit_decision(
            tick=state.tick,
            policy=f"{self.mode}_risk_fusion",
            candidate_actions=candidates,
            selected_action={
                "type": "defense_action" if selected_flags or defense.alert else "no_op",
                "actions": selected_flags,
                "active_link": defense.active_link.value,
                "risk_score": defense.risk_score,
                "alert": defense.alert,
                "decision_basis": defense.decision_basis,
            },
            reason=defense.alert or "monitoring state; no defense action required",
            feedback={
                "detection_tick": self.policy.alert_tick,
                "recovery_tick": self.policy.recovery_tick,
                "closed_simulation_only": True,
            },
        )
        return defense

    def attach_feedback(self, feedback: dict[str, Any]) -> None:
        self.runtime.attach_feedback(feedback)

    def _extract_mission_features(self, *, state: MissionState) -> list[float]:
        policy = self._ml_policy()
        return policy.extract_features(state)

    def _predict_mission_risk(self, *, features: list[float]) -> RiskPrediction:
        policy = self._ml_policy()
        return RiskPrediction(
            probability=policy.predict_ml_risk(features),
            model_backend=self._model_backend(),
            feature_count=len(features),
        )

    def _assess_mission_risk(
        self,
        *,
        state: MissionState,
        prediction: RiskPrediction | None,
    ) -> dict[str, Any]:
        if self.mode == "ml":
            if prediction is None:
                raise ValueError("TSRA-ML risk fusion requires a model prediction")
            return self._ml_policy().assess_state(
                state,
                ml_risk=prediction.probability,
                feature_count=prediction.feature_count,
            )
        return self.policy.assess_state(state)

    def _select_defense_action(
        self,
        *,
        state: MissionState,
        assessment: dict[str, Any],
    ) -> DefenseAction:
        return self.policy.choose_action(state, assessment)

    def _ml_policy(self) -> MLTSRARLite:
        if not isinstance(self.policy, MLTSRARLite):
            raise TypeError("ML policy tool called for a non-ML defense agent")
        return self.policy

    def _model_backend(self) -> str:
        policy = self._ml_policy()
        return sklearn_backend_name(policy.sklearn_model)

    @staticmethod
    def _state_input_summary(kwargs: dict[str, Any]) -> dict[str, Any]:
        state: MissionState = kwargs["state"]
        return {
            "tick": state.tick,
            "active_link": state.active_link.value,
            "satcom_health": round(state.satcom_health, 4),
            "queue_depth": state.queue_depth,
            "critical_queue_depth": state.critical_queue_depth,
        }

    def _risk_input_summary(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        state: MissionState = kwargs["state"]
        prediction: RiskPrediction | None = kwargs["prediction"]
        return {
            "tick": state.tick,
            "model_backend": prediction.model_backend if prediction else "none",
            "ml_risk": round(prediction.probability, 4) if prediction else None,
            "satcom_health": round(state.satcom_health, 4),
            "stale_ratio_window": round(state.stale_ratio_window, 4),
            "critical_latency_window": round(state.critical_latency_window, 4),
        }

    @staticmethod
    def _defense_output_summary(defense: DefenseAction) -> dict[str, Any]:
        return {
            "active_link": defense.active_link.value,
            "priority_boost": defense.priority_boost,
            "minimum_mode": defense.minimum_mode,
            "stale_badge": defense.stale_badge,
            "quarantine": defense.quarantine,
            "pace_transition": defense.pace_transition,
            "risk_score": defense.risk_score,
            "model_influenced_actions": defense.decision_basis.get(
                "model_influenced_actions",
                [],
            ),
            "guardrail_triggered_actions": defense.decision_basis.get(
                "guardrail_triggered_actions",
                [],
            ),
        }

    @staticmethod
    def _candidate_actions(defense: DefenseAction) -> list[dict[str, Any]]:
        basis = defense.decision_basis
        triggers = basis.get("action_triggers", {})
        rows = [
            ("priority_boost", defense.priority_boost, None),
            ("minimum_mode", defense.minimum_mode, None),
            ("stale_badge", defense.stale_badge, None),
            ("pace_transition", defense.pace_transition, defense.active_link.value),
            ("quarantine", defense.quarantine, None),
        ]
        return [
            {
                "action": action,
                "selected": selected,
                "target_link": target,
                "risk_score": defense.risk_score,
                "trigger_reasons": triggers.get(action, []),
                "model_influenced": action in basis.get("model_influenced_actions", []),
                "guardrail_triggered": action in basis.get("guardrail_triggered_actions", []),
            }
            for action, selected, target in rows
        ]
