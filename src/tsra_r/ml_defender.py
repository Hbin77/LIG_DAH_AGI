from __future__ import annotations

import pickle
from pathlib import Path

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
    ) -> None:
        self.rule = RuleTSRAR(mode="full")
        self.threshold = threshold
        self.defense_window_sec = defense_window_sec
        self.alert_cooldown_sec = alert_cooldown_sec
        self.active_defense_until = 0.0
        self.last_alert_time = -10_000.0
        if model_path.exists():
            with model_path.open("rb") as f:
                self.model = pickle.load(f)
        else:
            self.model = None
        self.runtime = AgentRuntime(
            agent_name="TSRA-R-ML",
            goal="open reactive defense windows when anomaly probability exceeds threshold",
        )
        self.runtime.register_tool(
            "predict_attack_probability",
            "Predict attack-induced degradation probability from mission state features",
            self._predict_attack_probability,
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
        events: list[DefenseEvent] = []
        opened_window = False

        if probability >= self.threshold:
            self.active_defense_until = max(
                self.active_defense_until,
                state.time_sec + self.defense_window_sec,
            )
            opened_window = True
            if state.time_sec - self.last_alert_time >= self.alert_cooldown_sec:
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
                "eligible": probability >= self.threshold,
                "probability": round(probability, 6),
                "threshold": self.threshold,
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
        self.runtime.record_decision(
            time_sec=state.time_sec,
            policy="ml_anomaly_detector",
            observation=observation,
            candidate_actions=candidate_actions,
            tool_calls=tool_calls,
            selected_action=selected_action,
            reason=(
                "detector opened or maintained defense window"
                if opened_window or active_window
                else "probability below threshold and no active defense window"
            ),
            feedback={
                "probability": probability,
                "threshold": self.threshold,
                "opened_window": opened_window,
                "active_defense_until": self.active_defense_until,
                "event_count": len(events),
            },
        )
        return events

    def _predict_attack_probability(self, state: MissionState) -> float:
        features = state_features(state)
        return float(self.model.predict_proba([features])[0][1])
