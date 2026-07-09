from __future__ import annotations

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

    def decide(self, state: MissionState) -> AttackEvent | None:
        if state.time_sec < self.min_start_sec:
            return None
        if self.event_count >= self.max_events:
            return None
        if state.time_sec - self.last_attack_time < self.cooldown_sec:
            return None

        scored = []
        for candidate in generate_candidates(state):
            predicted = estimate_candidate_effect(state, candidate, horizon_sec=120)
            impact = predicted["mission_impact"]
            detectability = estimate_detectability(candidate, predicted)
            score = compute_attack_score(impact, detectability)
            scored.append((score, candidate, predicted, detectability))

        if not scored:
            return None

        best_score, best_candidate, best_prediction, detectability = max(
            scored, key=lambda item: item[0]
        )
        if best_score < self.attack_threshold:
            return None

        self.last_attack_time = state.time_sec
        self.event_count += 1
        best_prediction["detectability_score"] = detectability
        return AttackEvent(
            event_id=f"atk-{self.event_count:05d}",
            selected_at=state.time_sec,
            candidate=best_candidate,
            expected_impact=best_prediction,
            reason=best_candidate.reason,
            score=best_score,
        )
