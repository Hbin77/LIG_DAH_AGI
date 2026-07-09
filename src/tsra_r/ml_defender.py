from __future__ import annotations

import pickle
from pathlib import Path

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

    def decide(self, state: MissionState) -> list[DefenseEvent]:
        if self.model is None:
            return []

        features = state_features(state)
        probability = float(self.model.predict_proba([features])[0][1])
        events: list[DefenseEvent] = []

        if probability >= self.threshold:
            self.active_defense_until = max(
                self.active_defense_until,
                state.time_sec + self.defense_window_sec,
            )
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

        if state.time_sec <= self.active_defense_until:
            events.extend(self.rule.decide(state))

        return events
