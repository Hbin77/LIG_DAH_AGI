from __future__ import annotations

import argparse
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

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    ".github/workflows/dev-quality.yml",
    "scripts/build_submission_zip.py",
    "scripts/train_ml_policy.py",
    "scripts/train_sklearn_policy.py",
    "scripts/tune_ml_policy.py",
    "scripts/verify_submission_state.py",
    "src/tsra_agent/__init__.py",
    "src/tsra_agent/agents.py",
    "src/tsra_agent/cli.py",
    "src/tsra_agent/evaluator.py",
    "src/tsra_agent/ml_policy.py",
    "src/tsra_agent/models.py",
    "src/tsra_agent/runtime.py",
    "src/tsra_agent/simulator.py",
    "tests/test_simulation.py",
    "docs/agent_branch_comparison.md",
    "docs/architecture.md",
    "docs/evaluation_plan.md",
    "docs/report_writer_guide.md",
    "docs/safety_boundary.md",
    "examples/summary_multi_seed.json",
    "examples/incident_report_multi_seed.md",
    "examples/run_manifest_multi_seed.json",
    "models/tsra_ml_policy.json",
    "models/tsra_ml_policy_config.json",
    "models/tsra_ml_training_report.json",
    "models/tsra_ml_tuning_report.json",
    "models/tsra_final_selection_report.json",
    "models/tsra_sklearn_policy.joblib",
    "models/tsra_sklearn_training_report.json",
]

ZIP_REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "src/tsra_agent/agents.py",
    "src/tsra_agent/runtime.py",
    "src/tsra_agent/simulator.py",
    "src/tsra_agent/cli.py",
    "models/tsra_sklearn_policy.joblib",
    "models/tsra_sklearn_training_report.json",
    "examples/summary_multi_seed.json",
    "docs/report_writer_guide.md",
    "docs/safety_boundary.md",
    "tests/test_simulation.py",
    "scripts/build_submission_zip.py",
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
    "safety_boundary",
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


def read_first_jsonl(path: Path) -> dict[str, Any]:
    require(path.exists(), f"missing trace file: {display_path(path)}")
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return json.loads(line)
    raise AssertionError(f"empty trace file: {display_path(path)}")


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
    require(test_count >= 7, f"expected at least 7 tests, got {test_count}")
    return [f"compile=pass", f"unit_tests={test_count} pass"]


def check_model_and_example_evidence() -> list[str]:
    fallback_model = read_json(ROOT / "models/tsra_ml_policy.json")
    sklearn_report = read_json(ROOT / "models/tsra_sklearn_training_report.json")
    selection = read_json(ROOT / "models/tsra_final_selection_report.json")
    summary = read_json(ROOT / "examples/summary_multi_seed.json")

    require(fallback_model["metrics"]["validation_f1"] >= 0.99, "fallback model validation_f1 below 0.99")
    require(sklearn_report["metrics"]["validation_f1"] >= 0.99, "sklearn validation_f1 below 0.99")
    require(sklearn_report["metrics"]["validation_roc_auc"] >= 0.99, "sklearn ROC-AUC below 0.99")
    require(selection["final_five_seed_metrics"]["baseline_adjusted_resilience_gain_percent"] >= 85.0, "final resilience gain below 85%")
    require(selection["final_five_seed_metrics"]["false_alarm_rate"] == 0.0, "final false alarm rate must be zero")

    aggregate = summary["aggregate"]
    attacked = aggregate["attacked"]["mission_impact_score"]["mean"]
    rule_defended = aggregate["rule_defended"]["mission_impact_score"]["mean"]
    defended = aggregate["defended"]["mission_impact_score"]["mean"]
    ml_defended = aggregate["ml_defended"]["mission_impact_score"]["mean"]
    gain = aggregate["resilience_gain_percent"]["mean"]
    ml_gain = aggregate["ml_resilience_gain_percent"]["mean"]

    require(attacked > rule_defended > defended, "mission impact ordering must be attacked > rule > TSRA-R")
    require(ml_defended <= rule_defended, "TSRA-ML must beat rule defense")
    require(gain >= 85.0 and ml_gain >= 85.0, "TSRA-R/ML resilience gain below 85%")
    require(aggregate["guarded_baseline"]["false_alarm_rate"]["mean"] == 0.0, "guarded baseline false alarm must be zero")
    require(aggregate["ml_guarded_baseline"]["false_alarm_rate"]["mean"] == 0.0, "ML guarded baseline false alarm must be zero")

    return [
        f"sklearn_f1={sklearn_report['metrics']['validation_f1']} pass",
        f"mission_impact={attacked}->{rule_defended}->{defended} pass",
        f"resilience_gain={gain} ml={ml_gain} pass",
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
        require(manifest["schema_version"] == "tsra-run-manifest/v1", "manifest schema mismatch")
        require(manifest["safety_boundary"]["synthetic_mission_event_simulator_only"] is True, "manifest safety boundary missing")
        require("seed_<seed>/<experiment>_tsra_decision_traces.jsonl" in manifest["artifacts"], "manifest missing TSRA trace artifact")

        seed_dir = output_dir / "seed_7"
        aura_trace = read_first_jsonl(seed_dir / "attacked_aura_decision_traces.jsonl")
        tsra_trace = read_first_jsonl(seed_dir / "defended_tsra_decision_traces.jsonl")
        ml_trace = read_first_jsonl(seed_dir / "ml_defended_tsra_decision_traces.jsonl")
        for trace in [aura_trace, tsra_trace, ml_trace]:
            missing = TRACE_REQUIRED_FIELDS - set(trace)
            require(not missing, f"trace missing fields: {sorted(missing)}")
            require(trace["candidate_actions"], "trace has no candidate actions")
            require(trace["tool_calls"], "trace has no tool calls")
            require(SAFETY_TEXT in trace["safety_boundary"], "trace missing safety boundary")

        aggregate = summary["aggregate"]
        require(
            aggregate["attacked"]["mission_impact_score"]["mean"]
            > aggregate["rule_defended"]["mission_impact_score"]["mean"]
            > aggregate["defended"]["mission_impact_score"]["mean"],
            "smoke mission impact ordering failed",
        )
        require(aggregate["resilience_gain_percent"]["mean"] >= 85.0, "smoke TSRA-R resilience gain below 85%")
        require(aggregate["ml_resilience_gain_percent"]["mean"] >= 85.0, "smoke TSRA-ML resilience gain below 85%")

    return ["cli_smoke=pass", "decision_trace_schema=pass"]


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
    checks.extend(check_cli_smoke())
    checks.extend(check_safety_boundary())
    checks.extend(check_package_zip())

    print("DEV submission verification passed")
    for check in checks:
        print(f"- {check}")


if __name__ == "__main__":
    main()
