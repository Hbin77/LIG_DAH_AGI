from __future__ import annotations

import pickle
from pathlib import Path

from src.aura.candidate_generator import generate_candidates
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
    ) -> None:
        self.attack_threshold = attack_threshold
        self.cooldown_sec = cooldown_sec
        self.max_events = max_events
        self.min_start_sec = min_start_sec
        self.last_attack_time = -10_000.0
        self.event_count = 0
        if not model_path.exists():
            self.model = None
            self.fallback = RuleAURA(attack_threshold, cooldown_sec, max_events, min_start_sec)
        else:
            with model_path.open("rb") as f:
                self.model = pickle.load(f)
            self.fallback = None

    def decide(self, state: MissionState) -> AttackEvent | None:
        if self.model is None:
            return self.fallback.decide(state) if self.fallback else None
        if state.time_sec < self.min_start_sec:
            return None
        if self.event_count >= self.max_events:
            return None
        if state.time_sec - self.last_attack_time < self.cooldown_sec:
            return None

        scored = []
        for candidate in generate_candidates(state):
            features = candidate_features(state, candidate)
            predicted_impact = float(self.model.predict([features])[0])
            predicted = estimate_candidate_effect(state, candidate, horizon_sec=120)
            detectability = estimate_detectability(candidate, predicted)
            score = compute_attack_score(predicted_impact, detectability)
            predicted["mission_impact"] = predicted_impact
            predicted["detectability_score"] = detectability
            scored.append((score, candidate, predicted))

        if not scored:
            return None

        best_score, best_candidate, best_prediction = max(scored, key=lambda item: item[0])
        if best_score < self.attack_threshold:
            return None

        self.last_attack_time = state.time_sec
        self.event_count += 1
        return AttackEvent(
            event_id=f"ml-atk-{self.event_count:05d}",
            selected_at=state.time_sec,
            candidate=best_candidate,
            expected_impact=best_prediction,
            reason=f"ML impact predictor selected {best_candidate.attack_type}",
            score=best_score,
        )
