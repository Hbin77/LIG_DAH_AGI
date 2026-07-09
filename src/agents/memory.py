from __future__ import annotations

from collections import deque
from typing import Any

from src.agents.schema import AgentObservation, DecisionTrace


class AgentMemory:
    def __init__(self, max_observations: int = 24, max_decisions: int = 24) -> None:
        self.observations: deque[AgentObservation] = deque(maxlen=max_observations)
        self.decisions: deque[DecisionTrace] = deque(maxlen=max_decisions)
        self.belief_state: dict[str, Any] = {}

    def remember_observation(self, observation: AgentObservation) -> None:
        self.observations.append(observation)

    def remember_decision(self, trace: DecisionTrace) -> None:
        self.decisions.append(trace)

    def update_belief(self, key: str, value: Any) -> None:
        self.belief_state[key] = value

    def summary(self) -> dict[str, Any]:
        last_observation = self.observations[-1] if self.observations else None
        last_decision = self.decisions[-1] if self.decisions else None
        return {
            "observation_count": len(self.observations),
            "decision_count": len(self.decisions),
            "belief_state": dict(self.belief_state),
            "last_observed_at": last_observation.time_sec if last_observation else None,
            "last_selected_action": (
                last_decision.selected_action if last_decision else None
            ),
        }
