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
        threshold: float = 0.55,
    ) -> None:
        self.rule = RuleTSRAR(mode="full")
        self.threshold = threshold
        if model_path.exists():
            with model_path.open("rb") as f:
                self.model = pickle.load(f)
        else:
            self.model = None

    def decide(self, state: MissionState) -> list[DefenseEvent]:
        events = self.rule.decide(state)
        if self.model is None:
            return events

        features = state_features(state)
        probability = float(self.model.predict_proba([features])[0][1])
        if probability < self.threshold:
            return events

        actions = {event.action for event in events}
        if "priority_reroute" not in actions and state.critical_pending > 0:
            events.append(
                self.rule._event(
                    state,
                    "priority_reroute",
                    {
                        "until_sec": state.time_sec + 80,
                        "reason": f"ML anomaly detector probability={probability:.2f}",
                    },
                )
            )
        if "video_throttle" not in actions and state.video_queue_kb > 300:
            events.append(
                self.rule._event(
                    state,
                    "video_throttle",
                    {
                        "until_sec": state.time_sec + 70,
                        "reason": f"ML anomaly detector probability={probability:.2f}",
                    },
                )
            )
        return events

