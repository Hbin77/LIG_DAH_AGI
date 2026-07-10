from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "requirements-gpu.txt",
    "scripts/build_submission_zip.py",
    "scripts/train_ml_policy.py",
    "scripts/train_sklearn_policy.py",
    "scripts/train_aura_rollout_policy.py",
    "scripts/evaluate_aura_policy.py",
    "scripts/train_aura_mps_student.py",
    "scripts/evaluate_aura_mps_candidate.py",
    "scripts/summarize_holdout.py",
    "scripts/tune_ml_policy.py",
    "scripts/summarize_decision_traces.py",
    "scripts/verify_submission_state.py",
    "src/tsra_agent/__init__.py",
    "src/tsra_agent/agents.py",
    "src/tsra_agent/attack_agent.py",
    "src/tsra_agent/attack_ml_policy.py",
    "src/tsra_agent/cli.py",
    "src/tsra_agent/defense_agent.py",
    "src/tsra_agent/evaluator.py",
    "src/tsra_agent/ml_policy.py",
    "src/tsra_agent/models.py",
    "src/tsra_agent/runtime.py",
    "src/tsra_agent/simulator.py",
    "tests/test_simulation.py",
    "docs/agent_branch_comparison.md",
    "docs/agent_engineering_notes.md",
    "docs/aura_ml_engineering_record.md",
    "docs/aura_mps_scale_experiment.md",
    "docs/architecture.md",
    "docs/evaluation_plan.md",
    "docs/report_writer_guide.md",
    "docs/safety_boundary.md",
    "examples/summary_multi_seed.json",
    "examples/holdout_30_seed_summary.json",
    "examples/aura_ml_holdout_30_seed_summary.json",
    "examples/incident_report_multi_seed.md",
    "examples/run_manifest_multi_seed.json",
    "models/tsra_ml_policy.json",
    "models/tsra_ml_policy_config.json",
    "models/tsra_ml_training_report.json",
    "models/tsra_ml_tuning_report.json",
    "models/tsra_final_selection_report.json",
    "models/tsra_sklearn_policy.joblib",
    "models/tsra_sklearn_training_report.json",
    "models/aura_rollout_policy.joblib",
    "models/aura_rollout_training_report.json",
    "models/aura_ml_policy_config.json",
    "models/aura_mps_student.pt",
    "models/aura_mps_student_weights.npz",
    "models/aura_mps_student_metrics.json",
    "models/aura_mps_selection_report.json",
]

ZIP_REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "requirements-gpu.txt",
    "src/tsra_agent/agents.py",
    "src/tsra_agent/attack_agent.py",
    "src/tsra_agent/attack_ml_policy.py",
    "src/tsra_agent/defense_agent.py",
    "src/tsra_agent/runtime.py",
    "src/tsra_agent/simulator.py",
    "src/tsra_agent/cli.py",
    "models/tsra_sklearn_policy.joblib",
    "models/tsra_sklearn_training_report.json",
    "models/aura_rollout_policy.joblib",
    "models/aura_rollout_training_report.json",
    "models/aura_ml_policy_config.json",
    "models/aura_mps_student.pt",
    "models/aura_mps_student_weights.npz",
    "models/aura_mps_student_metrics.json",
    "models/aura_mps_selection_report.json",
    "examples/summary_multi_seed.json",
    "examples/holdout_30_seed_summary.json",
    "examples/aura_ml_holdout_30_seed_summary.json",
    "docs/agent_engineering_notes.md",
    "docs/aura_ml_engineering_record.md",
    "docs/aura_mps_scale_experiment.md",
    "docs/report_writer_guide.md",
    "docs/safety_boundary.md",
    "tests/test_simulation.py",
    "scripts/build_submission_zip.py",
    "scripts/summarize_decision_traces.py",
    "scripts/summarize_holdout.py",
    "scripts/train_aura_rollout_policy.py",
    "scripts/evaluate_aura_policy.py",
    "scripts/train_aura_mps_student.py",
    "scripts/evaluate_aura_mps_candidate.py",
    "scripts/verify_submission_state.py",
]

TRACE_REQUIRED_FIELDS = {
    "trace_id",
    "agent",
    "tick",
    "goal",
    "policy",
    "observation",
    "memory",
    "candidate_actions",
    "tool_calls",
    "selected_action",
    "reason",
    "feedback",
    "runtime",
    "safety_boundary",
}

TOOL_CALL_REQUIRED_FIELDS = {
    "tool_name",
    "purpose",
    "input_summary",
    "output_summary",
    "status",
    "safety_checked",
}

SAFETY_TEXT = "closed synthetic mission simulation"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.exists(), f"missing jsonl file: {display_path(path)}")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(rows, f"empty jsonl file: {display_path(path)}")
    return rows


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def check_branch(require_dev: bool) -> list[str]:
    checks = []
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    github_ref = os.environ.get("GITHUB_REF_NAME", "")
    github_base_ref = os.environ.get("GITHUB_BASE_REF", "")
    if require_dev:
        require(
            branch == "DEV" or github_ref == "DEV" or github_base_ref == "DEV",
            (
                "verification must run on DEV branch, "
                f"got branch={branch} github_ref={github_ref} github_base_ref={github_base_ref}"
            ),
        )
    remote_refs = run(["git", "ls-remote", "--heads", "origin", "DEV", "main"]).stdout
    require("refs/heads/DEV" in remote_refs, "origin/DEV is missing")
    require("refs/heads/main" in remote_refs, "origin/main is missing")
    checks.append(f"branch={branch} github_ref={github_ref or 'local'} github_base_ref={github_base_ref or 'none'}")
    checks.append("origin DEV/main refs=present")
    return checks


def check_clean_worktree(require_clean: bool) -> list[str]:
    if not require_clean:
        return []
    status = run(["git", "status", "--short", "--untracked-files=no"]).stdout.strip()
    require(not status, f"tracked worktree is not clean:\n{status}")
    return ["tracked_worktree=clean"]


def check_required_files() -> list[str]:
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        require(path.exists(), f"missing required file: {rel}")
        require(path.stat().st_size > 0, f"empty required file: {rel}")
    return [f"required_files={len(REQUIRED_FILES)} present"]


def check_compile_and_tests() -> list[str]:
    run([sys.executable, "-m", "compileall", "-q", "src", "scripts", "tests"])
    result = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    match = re.search(r"Ran\s+(\d+)\s+tests?", output)
    test_count = int(match.group(1)) if match else 0
    require(test_count >= 16, f"expected at least 16 tests, got {test_count}")
    return [f"compile=pass", f"unit_tests={test_count} pass"]


def check_model_and_example_evidence() -> list[str]:
    import sklearn

    fallback_model = read_json(ROOT / "models/tsra_ml_policy.json")
    fallback_report = read_json(ROOT / "models/tsra_ml_training_report.json")
    sklearn_report = read_json(ROOT / "models/tsra_sklearn_training_report.json")
    policy_config = read_json(ROOT / "models/tsra_ml_policy_config.json")["config"]
    tuning_report = read_json(ROOT / "models/tsra_ml_tuning_report.json")
    selection = read_json(ROOT / "models/tsra_final_selection_report.json")
    summary = read_json(ROOT / "examples/summary_multi_seed.json")

    require(
        version_tuple(sklearn.__version__) >= (1, 9, 0),
        f"scikit-learn runtime must be >=1.9.0 for the bundled model, got {sklearn.__version__}",
    )
    require(fallback_model["metrics"]["validation_f1"] >= 0.97, "fallback model validation_f1 below 0.97")
    require(fallback_report["dataset_generator_version"] == "overlap-balanced-v2", "fallback dataset provenance mismatch")
    require(sklearn_report["metrics"]["validation_f1"] >= 0.985, "sklearn validation_f1 below 0.985")
    require(sklearn_report["metrics"]["validation_roc_auc"] >= 0.999, "sklearn ROC-AUC below 0.999")
    require(sklearn_report["dataset_generator_version"] == "overlap-balanced-v2", "primary dataset provenance mismatch")
    require(sklearn_report["feature_count"] == 12, "primary model feature count must be 12")
    require("defense_alerted" not in sklearn_report["feature_names"], "post-decision defense_alerted leaked into model features")
    data_quality = sklearn_report["data_quality"]
    require(data_quality["missing_value_count"] == 0, "training data contains missing values")
    require(data_quality["out_of_range_value_count"] == 0, "training features violate normalized range")
    require(data_quality["class_balance_delta"] == 0, "training labels are not balanced")
    trajectory = sklearn_report["closed_loop_oracle_validation"]["conditions"]
    require(trajectory["attacked"]["f1"] >= 0.95, "attacked-trajectory oracle F1 below 0.95")
    require(trajectory["baseline"]["false_positive_rate"] <= 0.01, "baseline trajectory false-positive rate too high")
    require(trajectory["tsra_defended"]["f1"] >= 0.95, "TSRA-defended trajectory oracle F1 below 0.95")
    model_path = ROOT / "models/tsra_sklearn_policy.joblib"
    require(
        hashlib.sha256(model_path.read_bytes()).hexdigest() == sklearn_report["model_sha256"],
        "bundled sklearn model hash does not match training report",
    )
    require(selection["final_five_seed_metrics"]["baseline_adjusted_resilience_gain_percent"] >= 85.0, "final resilience gain below 85%")
    require(selection["final_five_seed_metrics"]["false_alarm_rate"] == 0.0, "final false alarm rate must be zero")
    require(policy_config == tuning_report["selected_config"], "runtime policy config differs from tuning selection")
    require(policy_config == selection["selected_policy_config"], "final selection report policy config mismatch")
    require(
        hashlib.sha256((ROOT / "models/tsra_ml_policy_config.json").read_bytes()).hexdigest()
        == tuning_report["selected_policy_config_sha256"],
        "policy config hash does not match tuning report",
    )
    require(
        tuning_report["model_provenance"]["sha256"] == sklearn_report["model_sha256"],
        "tuning report was produced against a different model artifact",
    )
    require(selection["model_provenance"]["sha256"] == sklearn_report["model_sha256"], "final selection model hash mismatch")
    require(selection["selected_policy_config_sha256"] == tuning_report["selected_policy_config_sha256"], "final selection config hash mismatch")
    require(
        tuning_report["validation_result"]["metrics"]["missing_model_influence_seed_count"] == 0,
        "tuning validation contains a seed with no ML influence",
    )
    require(
        tuning_report["validation_result"]["metrics"]["guarded_model_influenced_ticks"] == 0,
        "tuning validation has model-influenced actions under no attack",
    )

    aggregate = summary["aggregate"]
    attacked = aggregate["attacked"]["mission_impact_score"]["mean"]
    rule_defended = aggregate["rule_defended"]["mission_impact_score"]["mean"]
    defended = aggregate["defended"]["mission_impact_score"]["mean"]
    ml_defended = aggregate["ml_defended"]["mission_impact_score"]["mean"]
    ml_ablated = aggregate["ml_ablated"]["mission_impact_score"]["mean"]
    gain = aggregate["resilience_gain_percent"]["mean"]
    ml_gain = aggregate["ml_resilience_gain_percent"]["mean"]

    require(attacked > rule_defended > defended, "mission impact ordering must be attacked > rule > TSRA-R")
    require(ml_defended <= rule_defended, "TSRA-ML must beat rule defense")
    require(ml_defended < defended, "TSRA-ML must improve mission impact over TSRA-R")
    require(ml_defended < ml_ablated, "learned TSRA-ML must beat its zero-model ablation")
    require(ml_ablated - ml_defended >= 1.0, "ML causal contribution is below one impact point")
    require(gain >= 85.0 and ml_gain >= 85.0, "TSRA-R/ML resilience gain below 85%")
    require(aggregate["guarded_baseline"]["false_alarm_rate"]["mean"] == 0.0, "guarded baseline false alarm must be zero")
    require(aggregate["ml_guarded_baseline"]["false_alarm_rate"]["mean"] == 0.0, "ML guarded baseline false alarm must be zero")
    require(
        aggregate["ml_defended"]["defense_intervention_ticks"]["mean"]
        < aggregate["defended"]["defense_intervention_ticks"]["mean"],
        "TSRA-ML must reduce intervention ticks relative to TSRA-R",
    )
    require(
        aggregate["ml_defended"]["priority_boost_ticks"]["mean"]
        < aggregate["defended"]["priority_boost_ticks"]["mean"],
        "TSRA-ML must reduce priority-boost ticks relative to TSRA-R",
    )
    require(
        aggregate["ml_defended"]["model_influenced_ticks"]["mean"] > 0,
        "TSRA-ML must expose model-influenced closed-loop actions",
    )

    return [
        f"sklearn_runtime={sklearn.__version__} pass",
        (
            f"sklearn_f1={sklearn_report['metrics']['validation_f1']} "
            f"trajectory_f1={trajectory['attacked']['f1']} pass"
        ),
        f"mission_impact={attacked}->{rule_defended}->{defended} pass",
        f"resilience_gain={gain} ml={ml_gain} pass",
        (
            "agent_action_economy="
            f"{aggregate['defended']['defense_intervention_ticks']['mean']}"
            "->"
            f"{aggregate['ml_defended']['defense_intervention_ticks']['mean']} pass"
        ),
        f"ml_ablation_impact={ml_ablated}->{ml_defended} pass",
    ]


def version_tuple(version: str) -> tuple[int, int, int]:
    parts = []
    for piece in version.split(".")[:3]:
        match = re.match(r"(\d+)", piece)
        parts.append(int(match.group(1)) if match else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def check_aura_model_evidence() -> list[str]:
    from joblib import load

    model_path = ROOT / "models/aura_rollout_policy.joblib"
    report_path = ROOT / "models/aura_rollout_training_report.json"
    config_path = ROOT / "models/aura_ml_policy_config.json"
    report = read_json(report_path)
    config = read_json(config_path)
    model = load(model_path)

    require(report["schema_version"] == "aura-rollout-training/v1", "AURA training schema mismatch")
    require(report["dataset_generator_version"] == "counterfactual-rollout-v1", "AURA dataset provenance mismatch")
    require(report["feature_count"] == 28, "AURA feature count must be 28")
    require(getattr(model, "n_features_in_", None) == 28, "AURA bundled model feature contract mismatch")
    require(getattr(model, "n_jobs", None) == 1, "AURA model inference must use n_jobs=1")
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    require(model_hash == report["model_sha256"], "AURA model hash differs from training evidence")
    require(config["model_sha256"] == model_hash, "AURA config references a different model")
    require(config["config"]["commitment_ticks"] == 4.0, "AURA commitment must be four ticks")

    split = report["split_contract"]
    require(split["seed_overlap"] == [], "AURA train and validation seeds overlap")
    require(split["row_random_split"] is False, "AURA evidence must not use row-random split")
    train = report["dataset"]["train"]
    validation = report["dataset"]["validation"]
    require(train["rows"] == 1440 and train["groups"] == 360, "AURA train grain mismatch")
    require(validation["rows"] == 576 and validation["groups"] == 144, "AURA validation grain mismatch")
    for profile in (train, validation):
        require(profile["missing_value_count"] == 0, "AURA features contain missing values")
        require(profile["out_of_range_feature_count"] == 0, "AURA normalized feature range violation")
    require(
        validation["conflicting_duplicate_feature_row_rate"] > 0.0,
        "AURA data evidence must expose conflicting observable labels",
    )

    learned = report["metrics"]["validation"]
    rule = report["metrics"]["validation_rule_ranker"]
    zero = report["metrics"]["validation_zero_model"]
    require(learned["top1_optimal_rate"] >= 0.70, "AURA top-1 optimal rate below 0.70")
    require(
        learned["top1_optimal_rate"] > rule["top1_optimal_rate"] > zero["top1_optimal_rate"],
        "AURA learned/rule/zero ranking order failed",
    )
    require(
        learned["mean_selection_regret"] < rule["mean_selection_regret"] < zero["mean_selection_regret"],
        "AURA learned/rule/zero selection-regret order failed",
    )
    return [
        (
            "aura_candidate_ranking="
            f"{learned['top1_optimal_rate']} rule={rule['top1_optimal_rate']} pass"
        ),
        f"aura_model_sha256={model_hash[:12]} feature_count=28 pass",
    ]


def check_aura_mps_evidence() -> list[str]:
    from src.tsra_agent.attack_ml_policy import load_mps_student_model

    checkpoint_path = ROOT / "models/aura_mps_student.pt"
    portable_path = ROOT / "models/aura_mps_student_weights.npz"
    metrics = read_json(ROOT / "models/aura_mps_student_metrics.json")
    selection = read_json(ROOT / "models/aura_mps_selection_report.json")
    primary = read_json(ROOT / "models/aura_rollout_training_report.json")

    require(metrics["schema_version"] == "aura-mps-scale/v1", "AURA MPS metrics schema mismatch")
    require(metrics["runtime"]["device"] == "mps", "AURA GPU experiment did not use MPS")
    require(metrics["runtime"]["mps_built"] is True, "AURA MPS backend was not built")
    require(metrics["runtime"]["mps_available"] is True, "AURA MPS backend was unavailable")
    scale = metrics["training_scale"]
    require(scale["sample_passes_per_epoch"] == 1_000_000, "AURA MPS epoch scale mismatch")
    require(scale["epochs"] == 20 and scale["total_sample_passes"] == 20_000_000, "AURA MPS total scale mismatch")
    require(scale["unique_candidate_claim"] is False, "AURA MPS scale must not claim unique candidates")
    provenance = metrics["dataset_provenance"]
    require(provenance["unique_train_rows"] == 1440, "AURA MPS unique train row count mismatch")
    require(provenance["unique_validation_rows"] == 576, "AURA MPS validation row count mismatch")
    require(provenance["matches_primary_training_report"] is True, "AURA MPS dataset provenance mismatch")
    require(provenance["train_sha256"] == primary["dataset"]["train_sha256"], "AURA MPS train hash mismatch")
    require(provenance["validation_sha256"] == primary["dataset"]["validation_sha256"], "AURA MPS validation hash mismatch")
    require(metrics["model_sha256"] == hashlib.sha256(checkpoint_path.read_bytes()).hexdigest(), "AURA MPS checkpoint hash mismatch")
    require(metrics["portable_export_sha256"] == hashlib.sha256(portable_path.read_bytes()).hexdigest(), "AURA MPS portable hash mismatch")
    require(metrics["validation"]["top1_optimal_rate"] > metrics["primary_extra_trees_comparison"]["top1_optimal_rate"], "AURA MPS candidate validation did not beat ExtraTrees")
    require(metrics["validation"]["mean_selection_regret"] < metrics["primary_extra_trees_comparison"]["mean_selection_regret"], "AURA MPS candidate regret did not beat ExtraTrees")

    model = load_mps_student_model()
    require(model.n_features_in_ == 28, "AURA MPS portable feature contract mismatch")
    predictions = model.predict([[0.0] * 28])
    require(len(predictions) == 1, "AURA MPS portable inference failed")

    require(selection["schema_version"] == "aura-mps-selection/v1", "AURA MPS selection schema mismatch")
    require(selection["model_provenance"]["mps_checkpoint_sha256"] == metrics["model_sha256"], "AURA MPS selection checkpoint mismatch")
    require(selection["model_provenance"]["mps_portable_sha256"] == metrics["portable_export_sha256"], "AURA MPS selection portable mismatch")
    decision = selection["promotion_decision"]
    require(decision["candidate_validation_pass"] is True, "AURA MPS candidate gate must pass")
    require(decision["promote_to_agent_runtime"] is False, "AURA MPS must remain unpromoted")
    require(decision["selected_runtime_backend"] == "sklearn_extra_trees_regressor", "AURA runtime backend selection mismatch")
    rule_delta = selection["closed_loop_development_gate"]["rule"]["paired_mps_minus_extra_trees"]
    require(rule_delta["mean"] <= -30.0 and rule_delta["wins"] == 0, "AURA MPS closed-loop rejection evidence missing")
    return [
        (
            "aura_mps_scale="
            f"{scale['total_sample_passes']} passes "
            f"top1={metrics['validation']['top1_optimal_rate']} "
            f"promotion=false pass"
        )
    ]


def check_cli_smoke() -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        output_dir = Path(tmp) / "dev_verify"
        run(
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
            ]
        )
        summary = read_json(output_dir / "summary.json")
        manifest = read_json(output_dir / "run_manifest.json")

        require(summary["scenario"] == "hybrid", "smoke summary scenario mismatch")
        require(summary["seeds"] == [7, 11], "smoke summary seed mismatch")
        require("defended" in summary["aggregate"], "summary missing defended aggregate")
        require("ml_defended" in summary["aggregate"], "summary missing ml_defended aggregate")
        require("ml_ablated" in summary["aggregate"], "summary missing ml_ablated aggregate")
        require(manifest["schema_version"] == "tsra-run-manifest/v2", "manifest schema mismatch")
        require(
            manifest["agent_runtime_contract"]["post_action_feedback_required"] is True,
            "manifest missing AgentRuntime feedback contract",
        )
        require(manifest["safety_boundary"]["synthetic_mission_event_simulator_only"] is True, "manifest safety boundary missing")
        require("seed_<seed>/<experiment>_tsra_decision_traces.jsonl" in manifest["artifacts"], "manifest missing TSRA trace artifact")

        seed_dir = output_dir / "seed_7"
        trace_sets = [
            read_jsonl(seed_dir / "attacked_aura_decision_traces.jsonl"),
            read_jsonl(seed_dir / "defended_tsra_decision_traces.jsonl"),
            read_jsonl(seed_dir / "ml_defended_tsra_decision_traces.jsonl"),
            read_jsonl(seed_dir / "ml_ablated_tsra_decision_traces.jsonl"),
        ]
        for traces in trace_sets:
            require(len(traces) == 80, f"expected 80 decision traces, got {len(traces)}")
            for trace in traces:
                validate_trace(trace)

        trace_csv = output_dir / "report_tables" / "decision_trace_summary.csv"
        trace_md = output_dir / "report_tables" / "decision_trace_summary.md"
        run(
            [
                sys.executable,
                "scripts/summarize_decision_traces.py",
                "--input-dir",
                str(output_dir),
                "--output-csv",
                str(trace_csv),
                "--output-md",
                str(trace_md),
            ]
        )
        with trace_csv.open(encoding="utf-8", newline="") as handle:
            trace_rows = list(csv.DictReader(handle))
        expected_trace_rows = sum(
            sum(1 for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip())
            for trace_path in output_dir.rglob("*_decision_traces.jsonl")
        )
        require(
            len(trace_rows) == expected_trace_rows,
            f"expected {expected_trace_rows} trace summary rows, got {len(trace_rows)}",
        )
        require(
            {row["agent"] for row in trace_rows}
            == {"AURA-lite", "Rule-Defense", "TSRA-R-lite", "TSRA-ML"},
            "trace summary agent coverage mismatch",
        )
        require(trace_md.exists() and trace_md.stat().st_size > 0, "trace summary markdown is missing")

        aggregate = summary["aggregate"]
        require(
            aggregate["attacked"]["mission_impact_score"]["mean"]
            > aggregate["rule_defended"]["mission_impact_score"]["mean"]
            > aggregate["defended"]["mission_impact_score"]["mean"],
            "smoke mission impact ordering failed",
        )
        require(aggregate["resilience_gain_percent"]["mean"] >= 85.0, "smoke TSRA-R resilience gain below 85%")
        require(aggregate["ml_resilience_gain_percent"]["mean"] >= 85.0, "smoke TSRA-ML resilience gain below 85%")
        require(
            aggregate["ml_defended"]["mission_impact_score"]["mean"]
            < aggregate["ml_ablated"]["mission_impact_score"]["mean"],
            "smoke learned model did not beat zero-model ablation",
        )
        require(
            aggregate["ml_defended"]["defense_intervention_ticks"]["mean"]
            < aggregate["defended"]["defense_intervention_ticks"]["mean"],
            "smoke TSRA-ML intervention count must differ from and improve on TSRA-R",
        )
        require(
            aggregate["ml_defended"]["model_influenced_ticks"]["mean"] > 0,
            "smoke run did not exercise ML-influenced defense actions",
        )

    return ["cli_smoke=pass", "decision_trace_schema=pass", "decision_trace_summary=pass"]


def check_aura_cli_smoke() -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        output_dir = Path(tmp) / "aura_ml_verify"
        run(
            [
                sys.executable,
                "-m",
                "src.tsra_agent.cli",
                "--scenario",
                "hybrid",
                "--attack-policy",
                "ml",
                "--ticks",
                "48",
                "--seed",
                "2003",
                "--output-dir",
                str(output_dir),
            ]
        )
        summary = read_json(output_dir / "summary.json")
        manifest = read_json(output_dir / "run_manifest.json")
        require(summary["attack_policy"] == "ml", "AURA-ML CLI summary policy mismatch")
        require(manifest["attack_policy"] == "ml", "AURA-ML manifest policy mismatch")
        traces = read_jsonl(output_dir / "attacked_aura_decision_traces.jsonl")
        require(len(traces) == 48, "AURA-ML smoke must contain 48 attack traces")
        require(all(trace["agent"] == "AURA-ML" for trace in traces), "AURA-ML trace identity mismatch")
        for trace in traces:
            validate_trace(trace)
        active = [
            trace
            for trace in traces
            if trace["selected_action"].get("mode") != "none"
        ]
        require(active, "AURA-ML smoke did not select an active action")
        require(
            any(trace["selected_action"]["decision_basis"]["model_influenced"] for trace in active),
            "AURA-ML smoke lacks model-influenced action",
        )
        require(
            any(
                trace["selected_action"]["decision_basis"]["selection_source"]
                == "memory_commitment"
                for trace in active
            ),
            "AURA-ML smoke did not execute memory commitment",
        )
    return ["aura_ml_cli_smoke=pass", "aura_ml_decision_trace=pass"]


def check_holdout_evidence() -> list[str]:
    holdout = read_json(ROOT / "examples/holdout_30_seed_summary.json")
    require(holdout["schema_version"] == "tsra-post-tuning-holdout/v1", "holdout schema mismatch")
    seeds = holdout["seeds"]
    require(holdout["seed_count"] == 30 and len(seeds) == 30 and len(set(seeds)) == 30, "holdout must contain 30 unique seeds")
    require(
        not (set(seeds) & set(holdout["development_seed_exclusion"])),
        "holdout overlaps model or policy development seeds",
    )
    require(
        holdout["model_sha256"]
        == hashlib.sha256((ROOT / "models/tsra_sklearn_policy.joblib").read_bytes()).hexdigest(),
        "holdout model hash mismatch",
    )
    require(
        holdout["policy_config_sha256"]
        == hashlib.sha256((ROOT / "models/tsra_ml_policy_config.json").read_bytes()).hexdigest(),
        "holdout policy hash mismatch",
    )
    aggregate = holdout["aggregate"]
    tsra_impact = aggregate["defended"]["mission_impact_score"]["mean"]
    ml_impact = aggregate["ml_defended"]["mission_impact_score"]["mean"]
    ablated_impact = aggregate["ml_ablated"]["mission_impact_score"]["mean"]
    require(ml_impact < tsra_impact, "30-seed holdout TSRA-ML did not beat TSRA-R")
    require(ml_impact < ablated_impact, "30-seed holdout learned model did not beat ablation")
    require(aggregate["ml_defended"]["model_influenced_ticks"]["mean"] > 0, "holdout lacks model influence")
    require(aggregate["ml_ablated"]["model_influenced_ticks"]["mean"] == 0, "holdout ablation has model influence")
    require(aggregate["ml_guarded_baseline"]["model_influenced_ticks"]["mean"] == 0, "holdout no-attack model influence is nonzero")
    require(aggregate["ml_guarded_baseline"]["false_alarm_rate"]["mean"] == 0, "holdout ML false alarm is nonzero")
    for comparison in holdout["paired_mission_impact"].values():
        require(comparison["count"] == 30, "holdout paired comparison count mismatch")
        require(comparison["bootstrap_95_percent_ci"][0] > 0, "holdout paired confidence interval crosses zero")
        require(comparison["wins"] >= 20, "holdout paired comparison wins below 20/30")
        require(comparison["losses"] > 0, "holdout artifact must preserve observed losing seeds")
    return [f"holdout_30_seed_impact={tsra_impact}->{ml_impact} ablation={ablated_impact} pass"]


def check_aura_holdout_evidence() -> list[str]:
    holdout_path = ROOT / "examples/aura_ml_holdout_30_seed_summary.json"
    holdout = read_json(holdout_path)
    require(holdout["schema_version"] == "aura-ml-holdout/v1", "AURA holdout schema mismatch")
    seeds = holdout["seeds"]
    require(holdout["seed_count"] == 30 and len(seeds) == 30 and len(set(seeds)) == 30, "AURA holdout must use 30 unique seeds")
    require(holdout["seed_provenance"]["holdout_overlap"] == [], "AURA holdout seed leakage")
    provenance = holdout["model_provenance"]
    require(
        provenance["sha256"]
        == hashlib.sha256((ROOT / "models/aura_rollout_policy.joblib").read_bytes()).hexdigest(),
        "AURA holdout model hash mismatch",
    )
    require(
        provenance["config_sha256"]
        == hashlib.sha256((ROOT / "models/aura_ml_policy_config.json").read_bytes()).hexdigest(),
        "AURA holdout config hash mismatch",
    )
    require(
        provenance["training_report_sha256"]
        == hashlib.sha256((ROOT / "models/aura_rollout_training_report.json").read_bytes()).hexdigest(),
        "AURA holdout training evidence hash mismatch",
    )
    require(holdout["acceptance"]["closed_loop_holdout_pass"] is True, "AURA holdout acceptance failed")
    conditions = holdout["conditions"]
    require(set(conditions) == {"none", "rule", "tsra", "ml"}, "AURA holdout context coverage mismatch")
    for context, evidence in conditions.items():
        versus_zero = evidence["paired_ml_minus_zero_model"]
        require(versus_zero["count"] == 30 and versus_zero["wins"] == 30, f"AURA zero-model ablation failed in {context}")
        require(versus_zero["bootstrap_95_ci"][0] > 0.0, f"AURA zero-model CI crosses zero in {context}")
        require(evidence["aura_ml_agent"]["model_influenced_ticks"]["mean"] > 0.0, f"AURA model influence missing in {context}")
    for context in ["rule", "tsra", "ml"]:
        versus_rule = conditions[context]["paired_ml_minus_rule"]
        require(versus_rule["bootstrap_95_ci"][0] > 0.0, f"AURA defended CI crosses zero in {context}")
        require(versus_rule["wins"] >= 25, f"AURA defended wins below 25/30 in {context}")
    none_comparison = conditions["none"]["paired_ml_minus_rule"]
    require(none_comparison["mean"] > 0.0, "AURA no-defense mean difference must be positive")
    require(none_comparison["bootstrap_95_ci"][0] <= 0.0, "AURA no-defense uncertainty must remain explicitly preserved")
    return [
        (
            "aura_holdout_30_seed_delta="
            f"rule:{conditions['rule']['paired_ml_minus_rule']['mean']} "
            f"tsra:{conditions['tsra']['paired_ml_minus_rule']['mean']} "
            f"ml:{conditions['ml']['paired_ml_minus_rule']['mean']} pass"
        )
    ]


def validate_trace(trace: dict[str, Any]) -> None:
    missing = TRACE_REQUIRED_FIELDS - set(trace)
    require(not missing, f"trace missing fields: {sorted(missing)}")
    require(trace["candidate_actions"], "trace has no candidate actions")
    require(trace["tool_calls"], "trace has no tool calls")
    require(SAFETY_TEXT in trace["safety_boundary"], "trace missing safety boundary")
    runtime = trace["runtime"]
    require(runtime.get("implementation") == "AgentRuntime", "trace was not produced by AgentRuntime")
    require(runtime.get("feedback_attached") is True, "trace missing environment feedback attachment")
    require(runtime.get("phase") == "feedback_attached", "runtime did not complete the feedback phase")
    require(runtime.get("tool_call_count") == len(trace["tool_calls"]), "runtime tool-call count mismatch")
    require(trace["feedback"].get("feedback_status") == "observed", "trace feedback is not observed")
    require("queue_depth_after_processing" in trace["feedback"], "trace missing closed-loop queue feedback")
    for tool_call in trace["tool_calls"]:
        missing_tool_fields = TOOL_CALL_REQUIRED_FIELDS - set(tool_call)
        require(not missing_tool_fields, f"tool call missing fields: {sorted(missing_tool_fields)}")
        require(tool_call["status"] == "ok", f"tool call status is not ok: {tool_call['status']}")
        require(tool_call["safety_checked"] is True, "tool call safety_checked must be true")
        require(isinstance(tool_call["input_summary"], dict), "tool input_summary must be an object")
        require(isinstance(tool_call["output_summary"], dict), "tool output_summary must be an object")
        require(tool_call["tool_name"] and tool_call["purpose"], "tool call name and purpose must be non-empty")
    if trace["agent"] == "TSRA-ML":
        backend = trace["selected_action"].get("decision_basis", {}).get("model_backend")
        if backend == "ablation_zero_model":
            validate_ml_ablation_trace(trace)
        else:
            validate_ml_trace(trace)
    if trace["agent"] in {"Rule-Defense", "TSRA-R-lite", "TSRA-ML"}:
        validate_defense_action_alignment(trace)
    if trace["agent"] in {"AURA-lite", "AURA-ML"}:
        validate_aura_trace(trace)
    if trace["agent"] == "AURA-ML":
        validate_aura_ml_trace(trace)


def validate_aura_trace(trace: dict[str, Any]) -> None:
    candidates = trace["candidate_actions"]
    require(len(candidates) >= 4, "AURA-lite trace must include no-op plus attack candidates")
    selected_candidates = [candidate for candidate in candidates if candidate.get("selected") is True]
    require(len(selected_candidates) == 1, "AURA-lite trace must mark exactly one selected candidate")
    selected = selected_candidates[0]
    max_score = max(candidate["score"] for candidate in candidates)
    require(selected["score"] == max_score, "AURA-lite selected candidate must have the highest score")
    require(trace["selected_action"]["score"] == selected["score"], "AURA-lite selected_action score mismatch")

    attack_tools = [tool for tool in trace["tool_calls"] if tool["tool_name"] == "select_attack_effect"]
    require(len(attack_tools) == 1, "AURA-lite trace must include one select_attack_effect tool call")
    output = attack_tools[0]["output_summary"]
    require(output["candidate_count"] == len(candidates), "AURA-lite tool candidate_count mismatch")
    require(output["selected_score"] == selected["score"], "AURA-lite tool selected_score mismatch")
    rank_tools = [tool for tool in trace["tool_calls"] if tool["tool_name"] == "rank_attack_candidates"]
    require(len(rank_tools) == 1, "AURA-lite trace must include one real candidate-ranking tool call")
    require(rank_tools[0]["output_summary"]["candidate_count"] == len(candidates), "AURA rank tool candidate count mismatch")


def validate_aura_ml_trace(trace: dict[str, Any]) -> None:
    basis = trace["selected_action"].get("decision_basis", {})
    required = {
        "policy_kind",
        "model_backend",
        "predicted_incremental_impact",
        "detectability_score",
        "rule_selected_action",
        "zero_model_selected_action",
        "model_influenced",
        "model_changed_rule_choice",
        "selection_source",
        "commitment_ticks",
    }
    missing = required - set(basis)
    require(not missing, f"AURA-ML decision basis missing fields: {sorted(missing)}")
    require(basis["policy_kind"] == "ml", "AURA-ML policy kind mismatch")
    require(basis["model_backend"] == "sklearn_extra_trees_regressor", "AURA-ML backend mismatch")
    require(basis["commitment_ticks"] == 4, "AURA-ML commitment mismatch")
    prediction_tools = [
        tool for tool in trace["tool_calls"] if tool["tool_name"] == "predict_attack_impacts"
    ]
    require(len(prediction_tools) == 1, "AURA-ML must execute one prediction tool per tick")
    output = prediction_tools[0]["output_summary"]
    require(output["model_backend"] == "sklearn_extra_trees_regressor", "AURA prediction backend mismatch")
    require(output["feature_count"] == 28, "AURA prediction feature count mismatch")


def validate_ml_trace(trace: dict[str, Any]) -> None:
    selected = trace["selected_action"]
    decision_basis = selected.get("decision_basis", {})
    required_basis = {
        "policy_kind",
        "model_backend",
        "ml_risk",
        "heuristic_risk",
        "fused_risk",
        "ml_weight",
        "heuristic_weight",
        "feature_count",
        "heuristic_only_component",
        "model_influenced_actions",
        "guardrail_triggered_actions",
    }
    missing_basis = required_basis - set(decision_basis)
    require(not missing_basis, f"TSRA-ML decision_basis missing fields: {sorted(missing_basis)}")
    require(decision_basis["policy_kind"] == "ml_risk_fusion", "TSRA-ML policy_kind mismatch")
    require(decision_basis["model_backend"] == "sklearn_hist_gradient_boosting", "TSRA-ML backend mismatch")
    for key in ["ml_risk", "heuristic_risk", "fused_risk", "ml_weight", "heuristic_weight"]:
        require(isinstance(decision_basis[key], (int, float)), f"TSRA-ML {key} must be numeric")
    require(decision_basis["feature_count"] > 0, "TSRA-ML feature_count must be positive")

    prediction_tools = [tool for tool in trace["tool_calls"] if tool["tool_name"] == "predict_mission_risk"]
    require(len(prediction_tools) == 1, "TSRA-ML trace must include one predict_mission_risk tool call")
    output = prediction_tools[0]["output_summary"]
    for key in ["ml_risk", "model_backend", "feature_count"]:
        require(key in output, f"predict_mission_risk output missing {key}")
    require(isinstance(output["ml_risk"], (int, float)), "predict_mission_risk ml_risk must be numeric")
    require(output["model_backend"] == "sklearn_hist_gradient_boosting", "predict_mission_risk backend mismatch")

    fusion_tools = [tool for tool in trace["tool_calls"] if tool["tool_name"] == "fuse_mission_risk"]
    require(len(fusion_tools) == 1, "TSRA-ML trace must include one fuse_mission_risk tool call")
    fusion_output = fusion_tools[0]["output_summary"]
    for key in ["ml_risk", "heuristic_risk", "fused_risk", "ml_weight", "heuristic_weight"]:
        require(key in fusion_output, f"fuse_mission_risk output missing {key}")
        require(isinstance(fusion_output[key], (int, float)), f"fuse_mission_risk {key} must be numeric")

    action_tools = [tool for tool in trace["tool_calls"] if tool["tool_name"] == "select_defense_action"]
    require(len(action_tools) == 1, "TSRA-ML trace must include one select_defense_action tool call")
    require(
        action_tools[0]["output_summary"]["model_influenced_actions"]
        == decision_basis["model_influenced_actions"],
        "TSRA-ML action attribution changed between tool output and selected action",
    )


def validate_ml_ablation_trace(trace: dict[str, Any]) -> None:
    basis = trace["selected_action"].get("decision_basis", {})
    require(basis.get("model_backend") == "ablation_zero_model", "ML ablation backend mismatch")
    require(basis.get("ml_risk") == 0.0, "ML ablation risk must be fixed to zero")
    require(not basis.get("model_influenced_actions"), "ML ablation emitted model-influenced actions")
    prediction_tools = [tool for tool in trace["tool_calls"] if tool["tool_name"] == "predict_mission_risk"]
    require(len(prediction_tools) == 1, "ML ablation must execute one prediction tool")
    require(prediction_tools[0]["output_summary"]["ml_risk"] == 0.0, "ML ablation tool risk must be zero")


def validate_defense_action_alignment(trace: dict[str, Any]) -> None:
    selected_action = trace["selected_action"]
    selected_candidates = [
        candidate["action"]
        for candidate in trace["candidate_actions"]
        if candidate.get("selected") is True and candidate.get("action")
    ]
    require(
        selected_action.get("actions") == selected_candidates,
        "TSRA selected_action actions must match selected candidate actions",
    )
    expected_type = (
        "defense_action"
        if selected_candidates or selected_action.get("alert")
        else "no_op"
    )
    require(selected_action.get("type") == expected_type, "TSRA selected_action type does not match candidate selection")
    require(trace["reason"], "TSRA trace requires a decision reason")


def check_safety_boundary() -> list[str]:
    combined = "\n".join(
        (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
        for rel in [
            "README.md",
            "docs/safety_boundary.md",
            "docs/report_writer_guide.md",
            "docs/architecture.md",
        ]
    ).lower()
    required_phrases = [
        "synthetic mission",
        "no exploit",
        "no operational rf",
        "no equipment-specific",
    ]
    for phrase in required_phrases:
        require(phrase in combined, f"safety documentation missing phrase: {phrase}")
    return ["safety_boundary=pass"]


def check_documented_numbers() -> list[str]:
    canonical_tokens = [
        "82.162",
        "61.228",
        "15.306",
        "12.926",
        "15.180",
        "90.374",
        "93.600",
        "2.254",
        "0.9884",
        "0.0629",
    ]
    docs = {
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "docs/report_writer_guide.md": (ROOT / "docs/report_writer_guide.md").read_text(encoding="utf-8"),
        "docs/evaluation_plan.md": (ROOT / "docs/evaluation_plan.md").read_text(encoding="utf-8"),
    }
    for path, text in docs.items():
        for token in canonical_tokens:
            require(token in text, f"{path} missing canonical metric token {token}")
    aura_tokens = [
        "0.7361",
        "0.3264",
        "20.4437",
        "3.0890",
        "4.4077",
        "19.2633",
        "2.1193",
        "3.5283",
    ]
    aura_docs = {
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "docs/evaluation_plan.md": (ROOT / "docs/evaluation_plan.md").read_text(encoding="utf-8"),
        "docs/aura_ml_engineering_record.md": (ROOT / "docs/aura_ml_engineering_record.md").read_text(encoding="utf-8"),
    }
    for path, text in aura_docs.items():
        for token in aura_tokens:
            require(token in text, f"{path} missing AURA metric token {token}")
    mps_tokens = [
        "20,000,000",
        "11.0838",
        "0.7986",
        "0.2341",
        "-37.1930",
        "1,804,443.12",
    ]
    mps_docs = {
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "docs/aura_mps_scale_experiment.md": (ROOT / "docs/aura_mps_scale_experiment.md").read_text(encoding="utf-8"),
    }
    for path, text in mps_docs.items():
        for token in mps_tokens:
            require(token in text, f"{path} missing MPS metric token {token}")
    return ["documented_numbers=canonical"]


def check_no_tracked_archives() -> list[str]:
    tracked = run(["git", "ls-files", "dist"]).stdout.splitlines()
    tracked_zips = [path for path in tracked if path.endswith(".zip")]
    require(
        not tracked_zips,
        f"tracked dist ZIP files are stale-submission risks; generate ZIPs locally instead: {tracked_zips}",
    )
    return ["tracked_dist_archives=none"]


def check_package_zip() -> list[str]:
    result = run([sys.executable, "scripts/build_submission_zip.py"])
    zip_path = Path(result.stdout.strip().splitlines()[-1])
    if not zip_path.is_absolute():
        zip_path = ROOT / zip_path
    require(zip_path.exists(), f"package zip was not created: {zip_path}")
    require(zip_path.stat().st_size > 1_000_000, f"package zip unexpectedly small: {zip_path.stat().st_size}")

    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        for rel in ZIP_REQUIRED_FILES:
            require(rel in names, f"package zip missing {rel}")
        forbidden_prefixes = ("outputs/", "dist/", ".git/", "__pycache__/")
        forbidden = [name for name in names if name.startswith(forbidden_prefixes) or "/__pycache__/" in name]
        require(not forbidden, f"package zip contains forbidden entries: {forbidden[:8]}")
        nested_zips = [name for name in names if name.endswith(".zip")]
        require(not nested_zips, f"package zip contains nested zip files: {nested_zips[:8]}")
        macos_metadata = [name for name in names if name.endswith(".DS_Store") or name.startswith("__MACOSX/")]
        require(not macos_metadata, f"package zip contains macOS metadata: {macos_metadata[:8]}")

    return [f"package_zip={zip_path.relative_to(ROOT)} entries={len(names)} bytes={zip_path.stat().st_size} pass"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify DEV branch final TSRA-X/AURA-lite submission state.")
    parser.add_argument("--require-clean", action="store_true", help="Fail when tracked files are modified.")
    parser.add_argument("--require-dev", action="store_true", help="Fail unless running on DEV branch.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checks: list[str] = []
    checks.extend(check_branch(args.require_dev))
    checks.extend(check_clean_worktree(args.require_clean))
    checks.extend(check_required_files())
    checks.extend(check_compile_and_tests())
    checks.extend(check_model_and_example_evidence())
    checks.extend(check_aura_model_evidence())
    checks.extend(check_aura_mps_evidence())
    checks.extend(check_cli_smoke())
    checks.extend(check_aura_cli_smoke())
    checks.extend(check_holdout_evidence())
    checks.extend(check_aura_holdout_evidence())
    checks.extend(check_safety_boundary())
    checks.extend(check_documented_numbers())
    checks.extend(check_no_tracked_archives())
    checks.extend(check_package_zip())

    print("DEV submission verification passed")
    for check in checks:
        print(f"- {check}")


if __name__ == "__main__":
    main()
