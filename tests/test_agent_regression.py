from __future__ import annotations

import unittest
from pathlib import Path

from src.agents.runtime import AgentRuntime
from src.aura.ml_impact_predictor import MLAURA
from src.shared.schemas import LinkState, MissionState
from src.tsra_r.rule_defender import RuleTSRAR


class ConstantImpactModel:
    def __init__(self, value: float = 0.82) -> None:
        self.value = value

    def predict(self, rows: list[list[float]]) -> list[float]:
        return [self.value for _ in rows]


def make_links(
    *,
    satcom_latency_ms: float = 850.0,
    satcom_loss: float = 0.02,
) -> dict[str, LinkState]:
    return {
        "SATCOM": LinkState(
            name="SATCOM",
            available=True,
            bandwidth_mbps=4.0,
            base_latency_ms=satcom_latency_ms,
            jitter_ms=90.0,
            loss_rate=satcom_loss,
        ),
        "LTE": LinkState(
            name="LTE",
            available=True,
            bandwidth_mbps=8.0,
            base_latency_ms=180.0,
            jitter_ms=35.0,
            loss_rate=0.015,
        ),
        "MESH": LinkState(
            name="MESH",
            available=True,
            bandwidth_mbps=6.0,
            base_latency_ms=120.0,
            jitter_ms=30.0,
            loss_rate=0.01,
        ),
    }


def make_state(
    *,
    time_sec: float = 100.0,
    mission_phase: str = "air_defense_watch",
    active_link: str = "SATCOM",
    links: dict[str, LinkState] | None = None,
    total_queue_kb: float = 5200.0,
    critical_pending: int = 3,
    video_queue_kb: float = 2400.0,
    stale_data_ratio: float = 0.36,
    recent_p95_critical_latency_sec: float = 6.0,
    priority_inversion_rate: float = 0.12,
    defense_mode: str = "none",
    active_attack_types: list[str] | None = None,
    recent_attack_types: list[str] | None = None,
    active_defense_actions: list[str] | None = None,
    recent_defense_actions: list[str] | None = None,
) -> MissionState:
    return MissionState(
        time_sec=time_sec,
        mission_phase=mission_phase,
        active_link=active_link,
        links=links or make_links(),
        queue_count_by_type={
            "air_defense_alert": 1,
            "command": 1,
            "coordinate": 1,
            "telemetry": 3,
            "video": 2,
        },
        queue_kb_by_type={
            "air_defense_alert": 8.0,
            "command": 12.0,
            "coordinate": 10.0,
            "telemetry": 96.0,
            "video": video_queue_kb,
        },
        total_queue_kb=total_queue_kb,
        critical_pending=critical_pending,
        video_queue_kb=video_queue_kb,
        stale_data_ratio=stale_data_ratio,
        recent_p95_critical_latency_sec=recent_p95_critical_latency_sec,
        priority_inversion_rate=priority_inversion_rate,
        defense_mode=defense_mode,
        active_attack_count=len(active_attack_types or []),
        active_attack_types=active_attack_types or [],
        active_attack_targets=["SATCOM"] if active_attack_types else [],
        recent_attack_event_ids=["atk-regression-001"] if recent_attack_types else [],
        recent_attack_types=recent_attack_types or [],
        recent_attack_targets=["SATCOM"] if recent_attack_types else [],
        last_attack_time_sec=80.0 if (active_attack_types or recent_attack_types) else None,
        last_attack_type=(active_attack_types or recent_attack_types or [""])[0],
        last_attack_target="SATCOM" if (active_attack_types or recent_attack_types) else "",
        active_defense_actions=active_defense_actions or [],
        recent_defense_actions=recent_defense_actions or [],
        last_defense_time_sec=90.0 if (active_defense_actions or recent_defense_actions) else None,
        last_defense_action=(active_defense_actions or recent_defense_actions or [""])[0],
    )


class AgentRuntimeRegressionTests(unittest.TestCase):
    def test_runtime_records_tool_memory_and_previous_action_chain(self) -> None:
        runtime = AgentRuntime(agent_name="TEST", goal="exercise runtime contract")
        runtime.register_tool("add", "Add two values", lambda x, y: x + y)

        state = make_state(time_sec=5.0)
        observation = runtime.observe(state)
        tool_calls = []
        result = runtime.call_tool("add", tool_calls, x=2, y=3)
        self.assertEqual(result, 5)

        first_trace = runtime.record_decision(
            time_sec=state.time_sec,
            policy="unit_policy",
            observation=observation,
            candidate_actions=[{"action": "no_op", "score": 0.0}],
            tool_calls=tool_calls,
            selected_action={"type": "no_op", "reason": "initial wait"},
            reason="initial wait",
        )

        self.assertEqual(first_trace.trace_id, "test-trace-00001")
        self.assertEqual(first_trace.memory["observation_count"], 1)
        self.assertEqual(first_trace.memory["decision_count"], 0)
        self.assertEqual(first_trace.tool_calls[0].status, "ok")
        self.assertEqual(first_trace.tool_calls[0].input_summary, {"x": 2, "y": 3})

        next_state = make_state(time_sec=10.0)
        next_observation = runtime.observe(next_state)
        second_trace = runtime.record_decision(
            time_sec=next_state.time_sec,
            policy="unit_policy",
            observation=next_observation,
            candidate_actions=[{"action": "hold", "score": 0.1}],
            tool_calls=[],
            selected_action={"type": "hold"},
            reason="previous action should be visible",
        )

        self.assertEqual(second_trace.trace_id, "test-trace-00002")
        self.assertEqual(second_trace.memory["decision_count"], 1)
        self.assertEqual(
            second_trace.memory["last_selected_action"],
            {"type": "no_op", "reason": "initial wait"},
        )
        self.assertEqual(runtime.memory.summary()["decision_count"], 2)


class AuraMLRegressionTests(unittest.TestCase):
    def test_ml_aura_event_identity_score_formula_and_cooldown_gate(self) -> None:
        aura = MLAURA(
            model_path=Path("outputs/models/__missing_for_unit_test__.pkl"),
            attack_threshold=0.05,
            cooldown_sec=45.0,
            max_events=2,
            min_start_sec=0.0,
        )
        aura.model = ConstantImpactModel(0.82)
        aura.fallback = None

        state = make_state(
            time_sec=100.0,
            active_link="LTE",
            defense_mode="pace_switch",
            active_defense_actions=["pace_switch"],
            recent_defense_actions=["priority_reroute"],
        )
        event = aura.decide(state)
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.agent, "AURA-ML")
        self.assertEqual(event.event_id, "ml-atk-00001")

        trace = list(aura.runtime.memory.decisions)[-1]
        self.assertEqual(trace.agent, "AURA-ML")
        self.assertEqual(trace.selected_action["type"], "attack_event")
        self.assertEqual(trace.selected_action["event_id"], event.event_id)
        self.assertAlmostEqual(trace.selected_action["score"], round(event.score, 6))
        self.assertGreaterEqual(len(trace.candidate_actions), 4)

        selected_score = trace.selected_action["score"]
        top_candidate_score = max(row["score"] for row in trace.candidate_actions)
        self.assertAlmostEqual(selected_score, top_candidate_score)

        for row in trace.candidate_actions:
            expected_selection = (
                row["base_attack_score"]
                + row["objective_bonus"]
                + row["counter_defense_bonus"]
                - row["repeated_tactic_penalty"]
            )
            self.assertAlmostEqual(row["selection_score"], expected_selection, places=6)
            self.assertTrue(row["cross_agent_defense_context_used"])

        tool_names = [call.tool_name for call in trace.tool_calls]
        self.assertEqual(tool_names.count("predict_candidate_impact"), len(trace.candidate_actions))
        self.assertEqual(tool_names.count("estimate_candidate_effect"), len(trace.candidate_actions))
        self.assertEqual(tool_names.count("estimate_detectability"), len(trace.candidate_actions))

        cooldown_state = make_state(
            time_sec=120.0,
            active_link="LTE",
            defense_mode="pace_switch",
            active_defense_actions=["pace_switch"],
        )
        self.assertIsNone(aura.decide(cooldown_state))
        cooldown_trace = list(aura.runtime.memory.decisions)[-1]
        self.assertEqual(cooldown_trace.selected_action["type"], "no_op")
        self.assertIn("cooldown", cooldown_trace.reason)
        self.assertIn("defense_context", cooldown_trace.feedback)


class TsraRRegressionTests(unittest.TestCase):
    def test_tsra_priority_scores_event_ordering_and_cooldown_noop(self) -> None:
        defender = RuleTSRAR(mode="full")
        state = make_state(
            time_sec=100.0,
            links=make_links(satcom_latency_ms=1300.0, satcom_loss=0.06),
            active_attack_types=[
                "queue_pressure",
                "stale_cop_induction",
                "failover_chasing",
            ],
            recent_attack_types=["queue_pressure"],
        )

        events = defender.decide(state)
        self.assertGreaterEqual(len(events), 4)
        actions = [event.action for event in events]
        for expected_action in {
            "priority_reroute",
            "stale_badge",
            "video_throttle",
            "pace_switch",
        }:
            self.assertIn(expected_action, actions)

        scores = [event.details["defense_priority_score"] for event in events]
        self.assertEqual(scores, sorted(scores, reverse=True))

        trace = list(defender.runtime.memory.decisions)[-1]
        self.assertEqual(trace.selected_action["type"], "defense_events")
        candidates_by_action = {row["action"]: row for row in trace.candidate_actions}
        for event in events:
            candidate = candidates_by_action[event.action]
            self.assertTrue(candidate["eligible"])
            self.assertTrue(candidate["ready"])
            self.assertAlmostEqual(
                event.details["defense_priority_score"],
                candidate["score"],
                places=6,
            )
            self.assertAlmostEqual(
                candidate["score"],
                candidate["defense_base_score"] + candidate["attack_context_bonus"],
                places=6,
            )
            self.assertIn("related_attack_context", event.details)

        followup_state = make_state(
            time_sec=110.0,
            links=make_links(satcom_latency_ms=1300.0, satcom_loss=0.06),
            active_attack_types=[
                "queue_pressure",
                "stale_cop_induction",
                "failover_chasing",
            ],
            recent_attack_types=["queue_pressure"],
        )
        self.assertEqual(defender.decide(followup_state), [])
        followup_trace = list(defender.runtime.memory.decisions)[-1]
        self.assertEqual(followup_trace.selected_action["type"], "no_op")
        self.assertEqual(followup_trace.reason, "no defense action emitted")
        self.assertFalse(
            any(
                row["enabled"] and row["eligible"] and row["ready"]
                for row in followup_trace.candidate_actions
            )
        )


if __name__ == "__main__":
    unittest.main()
