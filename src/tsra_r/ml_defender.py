from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from src.agents.runtime import AgentRuntime
from src.agents.schema import ToolCallRecord
from src.shared.features import state_features
from src.shared.schemas import DefenseEvent, MissionState
from src.tsra_r.rule_defender import RuleTSRAR


class MLTSRAR:
    def __init__(
        self,
        model_path: Path = Path("outputs/models/tsra_detector.pkl"),
        threshold: float = 0.75,
        defense_window_sec: float = 70.0,
        alert_cooldown_sec: float = 25.0,
        mission_guard_window_sec: float = 45.0,
        guard_refresh_margin_sec: float = 20.0,
        early_guard_probability: float = 0.50,
        early_guard_risk_score: float = 0.85,
    ) -> None:
        self.rule = RuleTSRAR(mode="full")
        self.threshold = threshold
        self.defense_window_sec = defense_window_sec
        self.alert_cooldown_sec = alert_cooldown_sec
        self.mission_guard_window_sec = mission_guard_window_sec
        self.guard_refresh_margin_sec = guard_refresh_margin_sec
        self.early_guard_probability = early_guard_probability
        self.early_guard_risk_score = early_guard_risk_score
        self.active_defense_until = 0.0
        self.last_alert_time = -10_000.0
        if model_path.exists():
            with model_path.open("rb") as f:
                self.model = pickle.load(f)
        else:
            self.model = None
        self.runtime = AgentRuntime(
            agent_name="TSRA-R-ML",
            goal=(
                "open reactive defense windows when anomaly probability exceeds threshold "
                "or residual mission risk remains near window expiry"
            ),
        )
        self.runtime.register_tool(
            "predict_attack_probability",
            "Predict attack-induced degradation probability from mission state features",
            self._predict_attack_probability,
        )
        self.runtime.register_tool(
            "assess_mission_risk_guard",
            "Assess residual COP, queue, and link risk before closing a reactive defense window",
            self._assess_mission_risk_guard,
        )

    def bind_runtime(self, trace_path: Path) -> None:
        self.runtime.bind_trace_log(trace_path)

    def decide(self, state: MissionState) -> list[DefenseEvent]:
        observation = self.runtime.observe(state)
        tool_calls: list[ToolCallRecord] = []
        candidate_actions: list[dict] = []

        if self.model is None:
            self.runtime.record_decision(
                time_sec=state.time_sec,
                policy="ml_anomaly_detector",
                observation=observation,
                candidate_actions=candidate_actions,
                tool_calls=tool_calls,
                selected_action={"type": "no_op"},
                reason="no deployed detector model found",
                feedback={
                    "threshold": self.threshold,
                    "active_defense_until": self.active_defense_until,
                },
            )
            return []

        probability = self.runtime.call_tool(
            "predict_attack_probability",
            tool_calls,
            state=state,
        )
        mission_guard = self.runtime.call_tool(
            "assess_mission_risk_guard",
            tool_calls,
            state=state,
            probability=probability,
        )
        events: list[DefenseEvent] = []
        opened_window = False
        detector_triggered = probability >= self.threshold
        guard_triggered = bool(mission_guard["open_window"])

        if detector_triggered or guard_triggered:
            window_sec = (
                self.defense_window_sec
                if detector_triggered
                else self.mission_guard_window_sec
            )
            self.active_defense_until = max(
                self.active_defense_until,
                state.time_sec + window_sec,
            )
            opened_window = True
            if detector_triggered and state.time_sec - self.last_alert_time >= self.alert_cooldown_sec:
                self.last_alert_time = state.time_sec
                events.append(
                    self.rule._event(
                        state,
                        "ml_attack_alert",
                        {
                            "probability": probability,
                            "threshold": self.threshold,
                            "until_sec": self.active_defense_until,
                            "reason": "ML anomaly detector opened defense window",
                        },
                    )
                )

        candidate_actions.append(
            {
                "action": "open_defense_window",
                "eligible": detector_triggered or guard_triggered,
                "probability": round(probability, 6),
                "threshold": self.threshold,
                "detector_triggered": detector_triggered,
                "mission_guard_triggered": guard_triggered,
                "early_guard_triggered": mission_guard["early_guard_triggered"],
                "expiry_guard_triggered": mission_guard["expiry_guard_triggered"],
                "mission_guard_reason": mission_guard["reason"],
                "mission_guard_score": mission_guard["risk_score"],
                "active_defense_until": self.active_defense_until,
            }
        )

        active_window = state.time_sec < self.active_defense_until
        if active_window:
            events.extend(self.rule.decide(state))

        selected_action = (
            {
                "type": "defense_events",
                "events": [
                    {
                        "event_id": event.event_id,
                        "action": event.action,
                        "details": event.details,
                    }
                    for event in events
                ],
            }
            if events
            else {"type": "no_op"}
        )
        self.runtime.memory.update_belief("active_defense_until", self.active_defense_until)
        self.runtime.memory.update_belief("last_probability", probability)
        self.runtime.memory.update_belief("last_alert_time", self.last_alert_time)
        self.runtime.memory.update_belief("last_mission_guard_reason", mission_guard["reason"])
        self.runtime.memory.update_belief("last_mission_guard_score", mission_guard["risk_score"])
        self.runtime.memory.update_belief("last_early_guard_triggered", mission_guard["early_guard_triggered"])
        self.runtime.record_decision(
            time_sec=state.time_sec,
            policy="ml_anomaly_detector",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action=selected_action,
            reason=(
                self._decision_reason(
                    detector_triggered=detector_triggered,
                    guard_triggered=guard_triggered,
                    active_window=active_window,
                )
                if opened_window or active_window
                else "probability below threshold and no active defense window"
            ),
            feedback={
                "probability": probability,
                "threshold": self.threshold,
                "detector_triggered": detector_triggered,
                "mission_guard_triggered": guard_triggered,
                "early_guard_triggered": mission_guard["early_guard_triggered"],
                "expiry_guard_triggered": mission_guard["expiry_guard_triggered"],
                "mission_guard_reason": mission_guard["reason"],
                "mission_guard_score": mission_guard["risk_score"],
                "opened_window": opened_window,
                "active_defense_until": self.active_defense_until,
                "event_count": len(events),
            },
        )
        return events

    def _predict_attack_probability(self, state: MissionState) -> float:
        features = state_features(state)
        return float(self.model.predict_proba([features])[0][1])

    def _assess_mission_risk_guard(
        self,
        state: MissionState,
        probability: float,
    ) -> dict[str, Any]:
        had_prior_window = self.active_defense_until > 0.0
        time_to_window_end = self.active_defense_until - state.time_sec
        near_or_after_window_end = time_to_window_end <= self.guard_refresh_margin_sec

        stale_component = min(state.stale_data_ratio / 0.5, 1.0)
        inversion_component = min(state.priority_inversion_rate / 0.12, 1.0)
        queue_component = min(state.video_queue_kb / 1500.0, 1.0)
        latency_component = min(state.recent_p95_critical_latency_sec / 3.0, 1.0)
        risk_score = round(
            min(
                1.0,
                0.40 * stale_component
                + 0.25 * inversion_component
                + 0.20 * queue_component
                + 0.15 * latency_component,
            ),
            6,
        )

        reasons = []
        if state.stale_data_ratio >= 0.5:
            reasons.append("residual_stale_cop")
        if (
            state.critical_pending > 0
            and state.video_queue_kb > 500.0
            and state.priority_inversion_rate >= 0.08
        ):
            reasons.append("critical_queue_pressure")
        if self._active_link_degraded(state) and (
            state.critical_pending > 0
            or state.total_queue_kb > 4500.0
            or state.priority_inversion_rate >= 0.1
        ):
            reasons.append("residual_link_degradation")

        expiry_guard_triggered = (
            had_prior_window
            and near_or_after_window_end
            and bool(reasons)
            and probability < self.threshold
        )
        early_pressure_reasons = {"critical_queue_pressure", "residual_link_degradation"}
        early_guard_triggered = (
            not had_prior_window
            and probability >= self.early_guard_probability
            and probability < self.threshold
            and risk_score >= self.early_guard_risk_score
            and bool(early_pressure_reasons.intersection(reasons))
        )
        open_window = expiry_guard_triggered or early_guard_triggered
        reason = "+".join(reasons) if reasons else "none"
        if early_guard_triggered:
            reason = f"{reason}+early_mission_pressure_guard"
        return {
            "open_window": open_window,
            "reason": reason,
            "risk_score": risk_score,
            "had_prior_window": had_prior_window,
            "time_to_window_end_sec": round(time_to_window_end, 6),
            "near_or_after_window_end": near_or_after_window_end,
            "early_guard_triggered": early_guard_triggered,
            "expiry_guard_triggered": expiry_guard_triggered,
        }

    @staticmethod
    def _active_link_degraded(state: MissionState) -> bool:
        active = state.links[state.active_link]
        if state.active_link == "SATCOM":
            return (
                active.base_latency_ms > 1100
                or active.loss_rate > 0.055
                or state.total_queue_kb > 4500.0
            )
        return (
            active.base_latency_ms > 550
            or active.loss_rate > 0.04
            or state.total_queue_kb > 6500.0
        )

    @staticmethod
    def _decision_reason(
        *,
        detector_triggered: bool,
        guard_triggered: bool,
        active_window: bool,
    ) -> str:
        if detector_triggered and guard_triggered:
            return "detector and mission risk guard opened or maintained defense window"
        if detector_triggered:
            return "detector opened or maintained defense window"
        if guard_triggered:
            return "mission risk guard opened or maintained defense window"
        if active_window:
            return "active defense window maintained while downstream rule actions were evaluated"
        return "probability below threshold and no active defense window"
