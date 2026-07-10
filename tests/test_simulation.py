from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts.build_submission_zip import should_include
from src.tsra_agent.attack_agent import AURAAgent
from src.tsra_agent.attack_ml_policy import (
    ATTACK_FEATURE_NAMES,
    AURA_ML_TICKS,
    DEFAULT_ATTACK_CONFIG_PATH,
    DEFAULT_ATTACK_MODEL_PATH,
    AblatedAttackImpactModel,
    load_attack_model,
)
from src.tsra_agent.defense_agent import TSRAAgent
from src.tsra_agent.evaluator import resilience_gain
from src.tsra_agent.ml_policy import (
    AblatedRiskModel,
    DEFAULT_MODEL_PATH,
    DEFAULT_POLICY_CONFIG_PATH,
    DEFAULT_SKLEARN_MODEL_PATH,
    FEATURE_NAMES,
    generate_training_samples,
    load_model,
    load_policy_config,
    load_sklearn_model,
)
from src.tsra_agent.models import AttackMode, LinkName
from src.tsra_agent.runtime import (
    AgentRuntime,
    AgentToolExecutionError,
    TOOL_CALL_REQUIRED_FIELDS,
    closed_synthetic_tool_validator,
)
from src.tsra_agent.simulator import MissionSimulator


class SimulationMetricTests(unittest.TestCase):
    def test_baseline_has_no_detection_or_recovery_penalty(self) -> None:
        baseline = MissionSimulator(180, 7, AttackMode.NONE, defense_enabled=False).run("baseline")
        attacked = MissionSimulator(180, 7, AttackMode.HYBRID, defense_enabled=False).run("attacked")

        self.assertIsNone(baseline.metrics.attack_start_tick)
        self.assertIsNone(baseline.metrics.detection_time)
        self.assertLess(baseline.metrics.mission_impact_score, attacked.metrics.mission_impact_score)

    def test_hybrid_attack_creates_priority_inversion(self) -> None:
        attacked = MissionSimulator(180, 7, AttackMode.HYBRID, defense_enabled=False).run("attacked")

        self.assertGreater(attacked.metrics.priority_inversion_rate, 0)
        self.assertGreater(attacked.metrics.expired_messages, 0)

    def test_tsra_reduces_inversion_and_records_recovery(self) -> None:
        defended = MissionSimulator(
            180,
            7,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="tsra",
        ).run("defended")

        self.assertEqual(defended.metrics.priority_inversion_rate, 0)
        self.assertEqual(defended.metrics.detection_time, 1)
        self.assertEqual(defended.metrics.recovery_time, 3)
        self.assertGreater(defended.metrics.compressed_messages, 0)
        self.assertEqual(defended.metrics.expired_messages, 0)

    def test_tsra_outperforms_rule_defense(self) -> None:
        baseline = MissionSimulator(180, 7, AttackMode.NONE, defense_enabled=False).run("baseline")
        attacked = MissionSimulator(180, 7, AttackMode.HYBRID, defense_enabled=False).run("attacked")
        rule = MissionSimulator(
            180,
            7,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="rule",
        ).run("rule_defended")
        tsra = MissionSimulator(
            180,
            7,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="tsra",
        ).run("defended")

        self.assertLess(tsra.metrics.mission_impact_score, rule.metrics.mission_impact_score)
        self.assertGreater(
            resilience_gain(attacked.metrics, tsra.metrics, baseline.metrics),
            resilience_gain(attacked.metrics, rule.metrics, baseline.metrics),
        )

    def test_ml_model_is_trained_and_policy_is_competitive(self) -> None:
        self.assertTrue(DEFAULT_MODEL_PATH.exists())
        self.assertTrue(DEFAULT_POLICY_CONFIG_PATH.exists())
        self.assertTrue(DEFAULT_SKLEARN_MODEL_PATH.exists())
        model = load_model()
        policy_config = load_policy_config()
        sklearn_model = load_sklearn_model()
        self.assertGreaterEqual(model.metrics["validation_f1"], 0.97)
        self.assertLessEqual(policy_config["ml_priority_threshold"], 0.35)
        self.assertTrue(hasattr(sklearn_model, "predict_proba"))

        sklearn_report = Path("models/tsra_sklearn_training_report.json")
        tuning_report = Path("models/tsra_ml_tuning_report.json")
        report = json.loads(sklearn_report.read_text(encoding="utf-8"))
        tuning = json.loads(tuning_report.read_text(encoding="utf-8"))
        self.assertGreaterEqual(report["metrics"]["validation_f1"], 0.985)
        self.assertGreaterEqual(
            report["closed_loop_oracle_validation"]["conditions"]["attacked"]["f1"],
            0.95,
        )
        self.assertGreaterEqual(tuning["validation_result"]["metrics"]["resilience_gain_percent"], 70.0)

        baseline = MissionSimulator(180, 7, AttackMode.NONE, defense_enabled=False).run("baseline")
        attacked = MissionSimulator(180, 7, AttackMode.HYBRID, defense_enabled=False).run("attacked")
        tsra = MissionSimulator(
            180,
            7,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="tsra",
        ).run("defended")
        ml = MissionSimulator(
            180,
            7,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="ml",
        ).run("ml_defended")
        ml_ablated = MissionSimulator(
            180,
            7,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="ml",
            sklearn_model=AblatedRiskModel(),
        ).run("ml_ablated")

        self.assertEqual(ml.metrics.priority_inversion_rate, 0)
        self.assertEqual(ml.metrics.expired_messages, 0)
        self.assertGreater(ml.metrics.compressed_messages, 0)
        self.assertLessEqual(ml.metrics.backlog_messages, tsra.metrics.backlog_messages)
        self.assertLessEqual(ml.metrics.recovery_time, tsra.metrics.recovery_time)
        self.assertLess(ml.metrics.defense_intervention_ticks, tsra.metrics.defense_intervention_ticks)
        self.assertLess(ml.metrics.priority_boost_ticks, tsra.metrics.priority_boost_ticks)
        self.assertGreater(ml.metrics.model_influenced_ticks, 0)
        self.assertEqual(ml_ablated.metrics.model_influenced_ticks, 0)
        self.assertLess(ml.metrics.mission_impact_score, ml_ablated.metrics.mission_impact_score)
        self.assertEqual(tsra.metrics.model_influenced_ticks, 0)
        self.assertGreater(
            resilience_gain(attacked.metrics, ml.metrics, baseline.metrics),
            85.0,
        )

    def test_training_data_contains_both_classes(self) -> None:
        samples = generate_training_samples(200, 1234)
        labels = [sample.label for sample in samples]

        self.assertEqual(labels.count(0), 100)
        self.assertEqual(labels.count(1), 100)
        self.assertTrue(all(len(sample.features) == 12 for sample in samples))
        self.assertNotIn("defense_alerted", FEATURE_NAMES)

    def test_aura_rollout_model_uses_seed_split_and_improves_ranking(self) -> None:
        report_path = Path("models/aura_rollout_training_report.json")
        self.assertTrue(DEFAULT_ATTACK_MODEL_PATH.exists())
        self.assertTrue(DEFAULT_ATTACK_CONFIG_PATH.exists())
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))
        model = load_attack_model()

        self.assertEqual(report["feature_names"], ATTACK_FEATURE_NAMES)
        self.assertNotIn("defense_alerted", ATTACK_FEATURE_NAMES)
        self.assertEqual(len(ATTACK_FEATURE_NAMES), 27)
        self.assertEqual(report["split_contract"]["seed_overlap"], [])
        self.assertFalse(report["split_contract"]["row_random_split"])
        self.assertEqual(
            hashlib.sha256(DEFAULT_ATTACK_MODEL_PATH.read_bytes()).hexdigest(),
            report["model_sha256"],
        )
        self.assertEqual(model.n_jobs, 1)
        self.assertEqual(model.n_features_in_, len(ATTACK_FEATURE_NAMES))
        learned = report["metrics"]["validation"]
        rule = report["metrics"]["validation_rule_ranker"]
        self.assertGreaterEqual(learned["top1_optimal_rate"], 0.70)
        self.assertGreater(learned["top1_optimal_rate"], rule["top1_optimal_rate"])
        self.assertLess(learned["mean_selection_regret"], rule["mean_selection_regret"])
        self.assertGreater(
            report["dataset"]["validation"]["conflicting_duplicate_feature_row_rate"],
            0.0,
        )

    def test_aura_ml_executes_model_tool_and_beats_zero_model(self) -> None:
        learned = MissionSimulator(
            AURA_ML_TICKS,
            1103,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="tsra",
            attack_policy="ml",
        ).run("aura_ml")
        zero = MissionSimulator(
            AURA_ML_TICKS,
            1103,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="tsra",
            attack_policy="ml",
            attack_model=AblatedAttackImpactModel(),
        ).run("aura_zero")

        self.assertGreater(
            learned.metrics.mission_impact_score,
            zero.metrics.mission_impact_score,
        )
        self.assertEqual(len(learned.traces["aura"]), AURA_ML_TICKS)
        self.assertTrue(all(trace["agent"] == "AURA-ML" for trace in learned.traces["aura"]))
        prediction_calls = [
            tool
            for trace in learned.traces["aura"]
            for tool in trace["tool_calls"]
            if tool["tool_name"] == "predict_attack_impacts"
        ]
        self.assertEqual(len(prediction_calls), 25)
        self.assertEqual(
            len(prediction_calls),
            sum(
                trace["selected_action"]["decision_basis"]["model_inference_executed"]
                for trace in learned.traces["aura"]
            ),
        )
        active_traces = [
            trace
            for trace in learned.traces["aura"]
            if trace["selected_action"]["mode"] != AttackMode.NONE.value
        ]
        self.assertTrue(active_traces)
        self.assertTrue(
            all(
                not trace["selected_action"]["decision_basis"]["model_inference_executed"]
                for trace in learned.traces["aura"]
                if trace["tick"] < 35
                or trace["selected_action"]["decision_basis"]["selection_source"]
                == "memory_commitment"
            )
        )
        basis = active_traces[0]["selected_action"]["decision_basis"]
        self.assertEqual(basis["model_backend"], "sklearn_extra_trees_regressor")
        self.assertEqual(basis["commitment_ticks"], 4)
        self.assertTrue(basis["model_influenced"])
        self.assertTrue(
            any(
                trace["selected_action"]["decision_basis"]["selection_source"]
                == "memory_commitment"
                for trace in active_traces
            )
        )

    def test_aura_holdout_is_disjoint_and_positive_against_defenses(self) -> None:
        path = Path("examples/aura_ml_holdout_30_seed_summary.json")
        self.assertTrue(path.exists())
        holdout = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(holdout["seed_count"], 30)
        self.assertEqual(holdout["seed_provenance"]["holdout_overlap"], [])
        self.assertTrue(holdout["acceptance"]["closed_loop_holdout_pass"])
        self.assertEqual(
            holdout["model_provenance"]["sha256"],
            hashlib.sha256(DEFAULT_ATTACK_MODEL_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            holdout["model_provenance"]["config_sha256"],
            hashlib.sha256(DEFAULT_ATTACK_CONFIG_PATH.read_bytes()).hexdigest(),
        )
        for context in ["rule", "tsra", "ml"]:
            evidence = holdout["conditions"][context]
            self.assertGreater(
                evidence["paired_ml_minus_rule"]["bootstrap_95_ci"][0],
                0.0,
            )
            self.assertGreater(
                evidence["paired_ml_minus_zero_model"]["bootstrap_95_ci"][0],
                0.0,
            )
            self.assertGreater(
                evidence["aura_ml_agent"]["model_influenced_ticks"]["mean"],
                0.0,
            )

class CliArtifactTests(unittest.TestCase):
    def test_cli_rejects_out_of_scope_aura_ml(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.tsra_agent.cli",
                "--scenario",
                "hybrid",
                "--attack-policy",
                "ml",
                "--ticks",
                "80",
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scenario=hybrid and ticks=180", result.stderr)

    def test_cli_writes_summary_report_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "run"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.tsra_agent.cli",
                    "--scenario",
                    "hybrid",
                    "--ticks",
                    "80",
                    "--seeds",
                    "7,11",
                    "--output-dir",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("outputs:", result.stdout)
            summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
            manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["seeds"], [7, 11])
            self.assertIn("defended", summary["aggregate"])
            self.assertIn("ml_defended", summary["aggregate"])
            self.assertIn("ml_ablated", summary["aggregate"])
            self.assertEqual(manifest["schema_version"], "tsra-run-manifest/v2")
            self.assertTrue(manifest["agent_runtime_contract"]["post_action_feedback_required"])
            self.assertTrue((output_dir / "incident_report.md").exists())
            trace_csv = output_dir / "report_tables" / "decision_trace_summary.csv"
            trace_md = output_dir / "report_tables" / "decision_trace_summary.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/summarize_decision_traces.py",
                    "--input-dir",
                    str(output_dir),
                    "--output-csv",
                    str(trace_csv),
                    "--output-md",
                    str(trace_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            trace_rows = trace_csv.read_text(encoding="utf-8").splitlines()
            expected_trace_rows = sum(
                len(path.read_text(encoding="utf-8").splitlines())
                for path in output_dir.rglob("*_decision_traces.jsonl")
            )
            self.assertEqual(len(trace_rows), expected_trace_rows + 1)
            self.assertIn("AURA-lite", trace_csv.read_text(encoding="utf-8"))
            self.assertIn("TSRA-ML", trace_csv.read_text(encoding="utf-8"))
            self.assertTrue(trace_md.exists())
            trace_path = output_dir / "seed_7" / "defended_tsra_decision_traces.jsonl"
            self.assertTrue(trace_path.exists())
            first_trace = json.loads(trace_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("observation", first_trace)
            self.assertIn("memory", first_trace)
            self.assertTrue(first_trace["candidate_actions"])
            self.assertTrue(first_trace["tool_calls"])
            self.assertIn("selected_action", first_trace)
            self.assertIn("closed synthetic mission simulation", first_trace["safety_boundary"])

    def test_decision_traces_include_structured_tool_results(self) -> None:
        result = MissionSimulator(
            48,
            7,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="ml",
        ).run("ml_defended")

        for agent_name, traces in result.traces.items():
            self.assertEqual(len(traces), 48, agent_name)
            for trace in traces:
                self.assertTrue(trace["candidate_actions"])
                self.assertTrue(trace["tool_calls"])
                self.assertEqual(trace["runtime"]["implementation"], "AgentRuntime")
                self.assertEqual(trace["runtime"]["phase"], "feedback_attached")
                self.assertTrue(trace["runtime"]["feedback_attached"])
                self.assertEqual(trace["feedback"]["feedback_status"], "observed")
                self.assertIn("queue_depth_after_processing", trace["feedback"])
                for tool_call in trace["tool_calls"]:
                    self.assertTrue(TOOL_CALL_REQUIRED_FIELDS.issubset(tool_call), tool_call)
                    self.assertEqual(tool_call["status"], "ok")
                    self.assertIs(tool_call["safety_checked"], True)
                    self.assertTrue(tool_call["safety_check"]["passed"])
                    self.assertEqual(
                        tool_call["safety_check"]["check_id"],
                        "closed_synthetic_bounds/v1",
                    )
                    self.assertIsInstance(tool_call["input_summary"], dict)
                    self.assertIsInstance(tool_call["output_summary"], dict)
                    self.assertTrue(tool_call["tool_name"])
                    self.assertTrue(tool_call["purpose"])

        aura_traces = result.traces["aura"]
        for trace in aura_traces:
            self.assertGreaterEqual(len(trace["candidate_actions"]), 4)
            selected_candidates = [candidate for candidate in trace["candidate_actions"] if candidate["selected"]]
            self.assertEqual(len(selected_candidates), 1)
            selected = selected_candidates[0]
            max_score = max(candidate["score"] for candidate in trace["candidate_actions"])
            self.assertEqual(selected["score"], max_score)
            self.assertEqual(trace["selected_action"]["score"], selected["score"])
            attack_tool = next(tool for tool in trace["tool_calls"] if tool["tool_name"] == "select_attack_effect")
            self.assertEqual(attack_tool["output_summary"]["candidate_count"], len(trace["candidate_actions"]))
            self.assertEqual(attack_tool["output_summary"]["selected_score"], selected["score"])

        ml_traces = result.traces["tsra"]
        prediction_tools = [
            tool_call
            for trace in ml_traces
            for tool_call in trace["tool_calls"]
            if tool_call["tool_name"] == "predict_mission_risk"
        ]
        self.assertEqual(len(prediction_tools), 48)
        first_prediction = prediction_tools[0]
        self.assertEqual(first_prediction["input_summary"]["model_backend"], "sklearn_hist_gradient_boosting")
        for key in ["ml_risk", "model_backend", "feature_count"]:
            self.assertIn(key, first_prediction["output_summary"])

        fusion_tools = [
            tool_call
            for trace in ml_traces
            for tool_call in trace["tool_calls"]
            if tool_call["tool_name"] == "fuse_mission_risk"
        ]
        self.assertEqual(len(fusion_tools), 48)
        for key in ["ml_risk", "heuristic_risk", "fused_risk", "ml_weight", "heuristic_weight"]:
            self.assertIn(key, fusion_tools[0]["output_summary"])
            self.assertIsInstance(fusion_tools[0]["output_summary"][key], float)

        first_ml_action = ml_traces[0]["selected_action"]
        self.assertEqual(first_ml_action["decision_basis"]["policy_kind"], "ml_risk_fusion")
        self.assertEqual(first_ml_action["decision_basis"]["model_backend"], "sklearn_hist_gradient_boosting")
        self.assertTrue(
            any(
                trace["selected_action"]["decision_basis"]["model_influenced_actions"]
                for trace in ml_traces
            )
        )


class AgentRuntimeContractTests(unittest.TestCase):
    def test_runtime_executes_registered_tool_and_attaches_environment_feedback(self) -> None:
        invocations = []

        def score_state(*, value: int) -> dict[str, int]:
            invocations.append(value)
            return {"score": value * 2}

        runtime = AgentRuntime("Test-Agent", "prove runtime execution")
        runtime.register_tool(
            "score_state",
            "score a synthetic state",
            score_state,
            safety_validator=closed_synthetic_tool_validator,
            allowed_input_fields={"value"},
        )
        state = SimpleNamespace(
            tick=3,
            active_link=LinkName.SATCOM,
            satcom_health=1.0,
            radio_health=1.0,
            lte_health=1.0,
            mesh_health=1.0,
            queue_depth=1,
            critical_queue_depth=0,
            stale_ratio_window=0.0,
            critical_latency_window=0.0,
            priority_inversion_window=0.0,
            terminal_risk_window=0.0,
            source_trust_drop_window=0.0,
            pace_instability_window=0.0,
            current_attack=AttackMode.NONE,
        )

        runtime.begin_cycle(state)
        result = runtime.call_tool("score_state", value=4)
        self.assertEqual(result, {"score": 8})
        self.assertEqual(invocations, [4])
        trace = runtime.commit_decision(
            tick=3,
            policy="test_policy",
            candidate_actions=[{"action": "no_op", "selected": True}],
            selected_action={"type": "no_op"},
            reason="test",
        )
        runtime.attach_feedback({"outcome": "stable"})

        self.assertEqual(trace["tool_calls"][0]["input_summary"], {"value": 4})
        self.assertEqual(trace["tool_calls"][0]["output_summary"], {"score": 8})
        self.assertEqual(trace["feedback"]["outcome"], "stable")
        self.assertTrue(trace["runtime"]["feedback_attached"])
        self.assertNotIn("defense_alerted", trace["observation"]["signals"])

    def test_safety_validator_rejects_input_before_handler_execution(self) -> None:
        invocations = []

        def unsafe_handler(**kwargs):
            invocations.append(kwargs)
            return {"accepted": True}

        runtime = AgentRuntime("Test-Agent", "reject operational payloads")
        runtime.register_tool(
            "unsafe",
            "prove pre-execution safety validation",
            unsafe_handler,
            safety_validator=closed_synthetic_tool_validator,
            allowed_input_fields={"value"},
        )
        state = SimpleNamespace(
            tick=1,
            active_link=LinkName.SATCOM,
            satcom_health=1.0,
            radio_health=1.0,
            lte_health=1.0,
            mesh_health=1.0,
            queue_depth=0,
            critical_queue_depth=0,
            stale_ratio_window=0.0,
            critical_latency_window=0.0,
            priority_inversion_window=0.0,
            terminal_risk_window=0.0,
            source_trust_drop_window=0.0,
            pace_instability_window=0.0,
            current_attack=AttackMode.NONE,
        )
        runtime.begin_cycle(state)
        for kwargs in (
            {"shell_command": "rm -rf /"},
            {"command": "rm -rf /"},
            {"url": "https://example.invalid"},
            {"payload": "exploit code"},
            {"rf": "2.4 GHz"},
            {"destination": "10.0.0.1"},
            {"value": "rm -rf /"},
        ):
            with self.assertRaises(AgentToolExecutionError):
                runtime.call_tool("unsafe", **kwargs)
        self.assertEqual(invocations, [])
        for payload in (
            {"payload": object()},
            {"host_name": "10.0.0.1"},
            {"command": "rm -rf /"},
            {"url": "https://example.invalid"},
            {"rf": "2.4 GHz"},
            {"destination": "10.0.0.1"},
            {"duration": 999_999},
            [
                {"action": "none", "selected": True},
                {"action": "link_degradation", "selected": True},
            ],
        ):
            self.assertFalse(
                closed_synthetic_tool_validator("input", payload)["passed"],
                payload,
            )
        output_runtime = AgentRuntime("Test-Agent", "reject unsafe tool output")
        output_runtime.register_tool(
            "invalid_output",
            "prove post-execution safety validation",
            lambda: {"duration": 999_999},
            safety_validator=closed_synthetic_tool_validator,
            allowed_input_fields=set(),
        )
        output_runtime.begin_cycle(state)
        with self.assertRaises(AgentToolExecutionError) as raised:
            output_runtime.call_tool("invalid_output")
        failed_trace = raised.exception.tool_call
        self.assertEqual(failed_trace["status"], "error")
        self.assertFalse(failed_trace["safety_checked"])
        self.assertTrue(failed_trace["safety_check"]["output"]["violations"])

    def test_aura_ml_rejects_out_of_scope_runtime(self) -> None:
        with self.assertRaisesRegex(ValueError, "scenario=hybrid and ticks=180"):
            MissionSimulator(
                179,
                1103,
                AttackMode.HYBRID,
                defense_enabled=False,
                attack_policy="ml",
            )
        with self.assertRaisesRegex(ValueError, "scenario=hybrid and ticks=180"):
            AURAAgent(
                AttackMode.LINK_DEGRADATION,
                policy_kind="ml",
                impact_model=AblatedAttackImpactModel(),
                episode_ticks=180,
            )
        with self.assertRaisesRegex(ValueError, "scenario=hybrid and ticks=180"):
            AURAAgent(
                AttackMode.HYBRID,
                policy_kind="ml",
                impact_model=AblatedAttackImpactModel(),
            )
        with self.assertRaisesRegex(ValueError, "scenario=hybrid and ticks=180"):
            MissionSimulator(
                180,
                1103,
                AttackMode.LINK_DEGRADATION,
                defense_enabled=False,
                attack_policy="ml",
            )

    def test_model_hash_mismatch_is_rejected_before_deserialization(self) -> None:
        expected_aura = hashlib.sha256(DEFAULT_ATTACK_MODEL_PATH.read_bytes()).hexdigest()
        expected_tsra = hashlib.sha256(DEFAULT_SKLEARN_MODEL_PATH.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            aura_path = Path(tmp) / "aura.joblib"
            tsra_path = Path(tmp) / "tsra.joblib"
            aura_path.write_bytes(DEFAULT_ATTACK_MODEL_PATH.read_bytes() + b"tampered")
            tsra_path.write_bytes(DEFAULT_SKLEARN_MODEL_PATH.read_bytes() + b"tampered")
            with mock.patch("joblib.load") as loader:
                with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                    load_attack_model(aura_path, expected_sha256=expected_aura)
                with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                    load_sklearn_model(tsra_path, expected_sha256=expected_tsra)
                loader.assert_not_called()

    def test_attack_and_defense_agents_own_separate_runtimes(self) -> None:
        attack = AURAAgent(AttackMode.HYBRID)
        defense = TSRAAgent("ml")

        self.assertIsNot(attack.runtime, defense.runtime)
        self.assertEqual(attack.runtime.agent_name, "AURA-lite")
        self.assertEqual(defense.runtime.agent_name, "TSRA-ML")
        self.assertIn("rank_attack_candidates", attack.runtime.registered_tools)
        self.assertIn("predict_mission_risk", defense.runtime.registered_tools)

    def test_submission_package_excludes_local_macos_metadata(self) -> None:
        self.assertFalse(should_include(Path("docs/.DS_Store")))
        self.assertFalse(should_include(Path("src/__pycache__/module.pyc")))
        self.assertTrue(should_include(Path("src/tsra_agent/runtime.py")))

    def test_tsra_selected_actions_match_selected_candidates(self) -> None:
        for defense_mode, expected_agent in [("tsra", "TSRA-R-lite"), ("ml", "TSRA-ML")]:
            result = MissionSimulator(
                48,
                7,
                AttackMode.HYBRID,
                defense_enabled=True,
                defense_mode=defense_mode,
            ).run(f"{defense_mode}_defended")
            traces = result.traces["tsra"]
            self.assertTrue(traces)
            for trace in traces:
                self.assertEqual(trace["agent"], expected_agent)
                selected_candidates = [
                    candidate["action"]
                    for candidate in trace["candidate_actions"]
                    if candidate.get("selected") is True
                ]
                expected_type = (
                    "defense_action"
                    if selected_candidates or trace["selected_action"].get("alert")
                    else "no_op"
                )
                self.assertEqual(trace["selected_action"]["type"], expected_type)
                self.assertEqual(trace["selected_action"]["actions"], selected_candidates)
                self.assertTrue(trace["reason"])


if __name__ == "__main__":
    unittest.main()
