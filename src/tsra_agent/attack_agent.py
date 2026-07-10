from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agents import AURALite, MissionState
from .models import AttackAction, AttackMode, LinkName
from .runtime import AgentRuntime


@dataclass(frozen=True)
class AttackSelection:
    action: AttackAction
    selected_candidate: dict[str, Any]
    candidate_count: int


class AURAAgent:
    """Attack-side agent with its own runtime, memory, tools, and traces."""

    def __init__(self, scenario: AttackMode) -> None:
        self.policy = AURALite(scenario)
        self.runtime = AgentRuntime(
            agent_name="AURA-lite",
            goal="select bounded simulated mission-effect attacks",
        )
        self.runtime.register_tool(
            "rank_attack_candidates",
            "rank bounded synthetic attack-effect candidates from mission state and memory",
            self._rank_attack_candidates,
            input_summarizer=self._rank_input_summary,
            output_summarizer=lambda candidates: {
                "candidate_count": len(candidates),
                "eligible_count": sum(1 for row in candidates if row["eligible"]),
                "selected_action": next(row["action"] for row in candidates if row["selected"]),
                "selected_score": next(row["score"] for row in candidates if row["selected"]),
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
        )

    @property
    def attack_start(self) -> int:
        return self.policy.attack_start

    @property
    def max_pulses(self) -> int:
        return self.policy.max_pulses

    def decide(self, state: MissionState) -> AttackAction:
        self.runtime.begin_cycle(state)
        memory_context = self.runtime.memory.summary()
        candidates = self.runtime.call_tool(
            "rank_attack_candidates",
            state=state,
            memory_context=memory_context,
        )
        selection: AttackSelection = self.runtime.call_tool(
            "select_attack_effect",
            candidates=candidates,
        )
        action = selection.action
        selected = selection.selected_candidate

        self.runtime.memory.update_belief("last_attack_mode", action.mode.value)
        self.runtime.memory.update_belief("last_target_link", action.target_link.value)
        self.runtime.memory.update_belief("last_attack_score", selected["score"])
        self.runtime.memory.update_belief(
            "active_attack_tick_count",
            int(self.runtime.memory.belief_state.get("active_attack_tick_count", 0))
            + int(action.mode != AttackMode.NONE),
        )
        self.runtime.commit_decision(
            tick=state.tick,
            policy="aura_lite_candidate_ranker",
            candidate_actions=candidates,
            selected_action={
                "type": "attack_action" if action.mode != AttackMode.NONE else "no_op",
                "mode": action.mode.value,
                "target_link": action.target_link.value,
                "intensity": round(action.intensity, 4),
                "score": selected["score"],
                "predicted_effect": selected["predicted_effect"],
            },
            reason=action.rationale,
            feedback={
                "closed_simulation_only": True,
                "attack_start": self.policy.attack_start,
                "max_pulses": self.policy.max_pulses,
            },
        )
        return action

    def attach_feedback(self, feedback: dict[str, Any]) -> None:
        self.runtime.attach_feedback(feedback)

    def _rank_attack_candidates(
        self,
        *,
        state: MissionState,
        memory_context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        candidates = self.policy.rank_candidates(state)
        last_mode = memory_context.get("belief_state", {}).get("last_attack_mode")
        for candidate in candidates:
            candidate["memory_adjustment"] = 0.0
            if (
                candidate["eligible"]
                and candidate["action"] != AttackMode.NONE.value
                and candidate["action"] == last_mode
            ):
                candidate["memory_adjustment"] = -0.01
                candidate["score"] = round(candidate["score"] - 0.01, 4)

        selected_index = max(
            range(len(candidates)),
            key=lambda index: candidates[index]["score"],
        )
        for index, candidate in enumerate(candidates):
            candidate["selected"] = index == selected_index
        return candidates

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
    def _rank_input_summary(kwargs: dict[str, Any]) -> dict[str, Any]:
        state: MissionState = kwargs["state"]
        memory_context = kwargs["memory_context"]
        return {
            "tick": state.tick,
            "scenario": state.current_attack.value,
            "active_link": state.active_link.value,
            "queue_depth": state.queue_depth,
            "critical_queue_depth": state.critical_queue_depth,
            "last_attack_mode": memory_context.get("belief_state", {}).get("last_attack_mode"),
            "previous_decision_count": memory_context.get("recent_decision_count", 0),
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
