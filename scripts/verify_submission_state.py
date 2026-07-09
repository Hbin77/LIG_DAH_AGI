from __future__ import annotations

import argparse
import csv
import subprocess
import zipfile
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "outputs" / "package" / "DAH2026_source_LIG_DAH_AGI.zip"
MANIFEST_PATH = ROOT / "outputs" / "package" / "submission_manifest.md"

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "scripts/build_submission_package.py",
    "scripts/verify_submission_state.py",
    "docs/process/COMPETITION_DIRECTION.md",
    "docs/process/NEXT_DEVELOPMENT_QUEUE.md",
    "docs/process/DEVELOPMENT_LOG.md",
    "docs/process/FINAL_QA.md",
    "docs/process/SUBMISSION_PACKAGE.md",
    "src/agents/runtime.py",
    "src/aura/rule_decision_engine.py",
    "src/tsra_r/rule_defender.py",
    "src/tsra_r/adaptive_defender.py",
    "src/experiments/battle_timeline.py",
    "src/experiments/incident_summary.py",
    "src/experiments/competition_alignment.py",
    "src/experiments/validate_event_contracts.py",
    "src/experiments/trace_quality_audit.py",
    "outputs/experiments/experiment_summary.csv",
    "outputs/batch/repeated_experiment_summary.csv",
    "outputs/batch/resilience_gain_summary.csv",
    "outputs/batch/tsra_action_ablation_summary.csv",
    "outputs/batch/adaptive_memory_summary.csv",
    "outputs/report_tables/agent_decision_trace_summary.csv",
    "outputs/report_tables/aura_coa_cards.csv",
    "outputs/report_tables/battle_timeline.csv",
    "outputs/report_tables/incident_summary.csv",
    "outputs/report_tables/competition_alignment_matrix.csv",
    "outputs/report_tables/competition_alignment_matrix.md",
    "outputs/report_tables/agent_contract_validation.csv",
    "outputs/report_tables/agent_contract_validation.md",
    "outputs/report_tables/decision_trace_quality_audit.csv",
    "outputs/report_tables/decision_trace_quality_audit.md",
    "outputs/figures/aura_tsra_architecture.png",
    "outputs/figures/batch_resilience_gain.png",
    "outputs/figures/tsra_action_ablation.png",
    "outputs/figures/adaptive_memory_comparison.png",
    "outputs/models/aura_impact_model_metrics.json",
    "outputs/models/tsra_detector_metrics.json",
]

ZIP_REQUIRED_FILES = REQUIRED_FILES + [
    "outputs/package/submission_manifest.md",
]


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def read_csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_required_files() -> list[str]:
    checked = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        require(path.exists(), f"missing required file: {rel}")
        require(path.stat().st_size > 0, f"empty required file: {rel}")
        checked.append(rel)
    return checked


def check_csv_outputs() -> list[str]:
    checks = []

    experiment_rows = read_csv("outputs/experiments/experiment_summary.csv")
    experiments = {row["experiment"] for row in experiment_rows}
    require(
        {"E1_baseline", "E3_rule_aura", "E5_rule_aura_tsra_r"}.issubset(experiments),
        f"experiment_summary missing baseline/core experiments: {sorted(experiments)}",
    )
    checks.append(f"experiment_summary rows={len(experiment_rows)}")

    repeated_rows = read_csv("outputs/batch/repeated_experiment_summary.csv")
    require(len(repeated_rows) >= 5, "repeated_experiment_summary has too few rows")
    checks.append(f"repeated_experiment_summary rows={len(repeated_rows)}")

    resilience_rows = read_csv("outputs/batch/resilience_gain_summary.csv")
    require(len(resilience_rows) >= 1, "resilience_gain_summary is empty")
    checks.append(f"resilience_gain_summary rows={len(resilience_rows)}")

    ablation_rows = read_csv("outputs/batch/tsra_action_ablation_summary.csv")
    require(len(ablation_rows) == 5, f"expected 5 TSRA ablation rows, got {len(ablation_rows)}")
    checks.append("tsra_action_ablation_summary rows=5")

    adaptive_rows = read_csv("outputs/batch/adaptive_memory_summary.csv")
    adaptive_conditions = {row["condition"] for row in adaptive_rows}
    require(
        adaptive_conditions == {"full_tsra_r", "adaptive_tsra_r"},
        f"unexpected adaptive conditions: {sorted(adaptive_conditions)}",
    )
    checks.append("adaptive_memory_summary conditions=full/adaptive")

    trace_rows = read_csv("outputs/report_tables/agent_decision_trace_summary.csv")
    require(len(trace_rows) >= 200, f"trace summary too small: {len(trace_rows)} rows")
    checks.append(f"agent_decision_trace_summary rows={len(trace_rows)}")

    contract_rows = read_csv("outputs/report_tables/agent_contract_validation.csv")
    require(len(contract_rows) == 49, f"expected 49 contract checks, got {len(contract_rows)}")
    failed_contracts = [
        f"{row['experiment']}:{row['contract']}"
        for row in contract_rows
        if row.get("status") != "pass"
    ]
    require(not failed_contracts, f"failed agent contracts: {failed_contracts[:8]}")
    required_contracts = {
        "attack_event_schema",
        "defense_event_schema",
        "metric_snapshot_schema",
        "mission_event_schema",
        "aura_decision_trace_schema",
        "tsra-r_decision_trace_schema",
        "agent_cross_contract",
    }
    observed_contracts = {row["contract"] for row in contract_rows}
    require(
        required_contracts.issubset(observed_contracts),
        f"agent contract validation missing contracts: {sorted(required_contracts - observed_contracts)}",
    )
    checks.append("agent_contract_validation rows=49 pass")

    trace_quality_rows = read_csv("outputs/report_tables/decision_trace_quality_audit.csv")
    require(
        len(trace_quality_rows) == 9,
        f"expected 9 trace quality audit rows, got {len(trace_quality_rows)}",
    )
    failed_trace_quality = [
        f"{row['experiment']}:{row['agent']}:{row['policy']}"
        for row in trace_quality_rows
        if row.get("status") != "pass"
    ]
    require(not failed_trace_quality, f"failed trace quality rows: {failed_trace_quality[:8]}")
    require(
        any(row["agent"].startswith("AURA") for row in trace_quality_rows),
        "trace quality audit has no AURA rows",
    )
    require(
        any(row["agent"].startswith("TSRA-R") for row in trace_quality_rows),
        "trace quality audit has no TSRA-R rows",
    )
    require(
        all(float(row["reason_coverage"]) == 1.0 for row in trace_quality_rows),
        "trace quality audit has incomplete reason coverage",
    )
    checks.append("decision_trace_quality_audit rows=9 pass")

    coa_rows = read_csv("outputs/report_tables/aura_coa_cards.csv")
    require(len(coa_rows) >= 10, f"COA cards too small: {len(coa_rows)} rows")
    require(
        all(has_safety_boundary(row.get("safety_boundary", "")) for row in coa_rows),
        "AURA COA cards missing simulation safety boundary",
    )
    checks.append(f"aura_coa_cards rows={len(coa_rows)}")

    battle_rows = read_csv("outputs/report_tables/battle_timeline.csv")
    battle_experiments = {row["experiment"] for row in battle_rows}
    require(
        battle_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected battle timeline experiments: {sorted(battle_experiments)}",
    )
    for experiment in battle_experiments:
        subset = [row for row in battle_rows if row["experiment"] == experiment]
        require(any(row["attack_events"] for row in subset), f"{experiment} has no attack events")
        require(any(row["defense_events"] for row in subset), f"{experiment} has no defense events")
    require(
        all("closed simulation" in row["safety_boundary"] for row in battle_rows),
        "battle timeline missing safety boundary",
    )
    checks.append(f"battle_timeline rows={len(battle_rows)}")

    incident_rows = read_csv("outputs/report_tables/incident_summary.csv")
    incident_experiments = {row["experiment"] for row in incident_rows}
    require(
        incident_experiments == {"E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r"},
        f"unexpected incident summary experiments: {sorted(incident_experiments)}",
    )
    for experiment in incident_experiments:
        subset = [row for row in incident_rows if row["experiment"] == experiment]
        require(3 <= len(subset) <= 5, f"{experiment} should have 3-5 incidents, got {len(subset)}")
        require(all(row["attack_summary"] for row in subset), f"{experiment} incident missing attack summary")
        require(all(row["defense_response"] for row in subset), f"{experiment} incident missing defense response")
    require(
        all("closed simulation" in row["safety_boundary"] for row in incident_rows),
        "incident summary missing safety boundary",
    )
    checks.append(f"incident_summary rows={len(incident_rows)}")

    alignment_rows = read_csv("outputs/report_tables/competition_alignment_matrix.csv")
    require(len(alignment_rows) == 10, f"expected 10 alignment rows, got {len(alignment_rows)}")
    incomplete_alignment = [
        row["alignment_id"]
        for row in alignment_rows
        if row.get("evidence_status") != "verified"
    ]
    require(not incomplete_alignment, f"incomplete alignment rows: {incomplete_alignment}")
    required_alignment_areas = {
        "Attack scenario",
        "Defense architecture",
        "AI agent architecture",
        "Attack-defense cooperation",
        "Safety boundary",
    }
    observed_alignment_areas = {row["scoring_area"] for row in alignment_rows}
    require(
        required_alignment_areas.issubset(observed_alignment_areas),
        f"alignment matrix missing required areas: {sorted(required_alignment_areas - observed_alignment_areas)}",
    )
    checks.append("competition_alignment_matrix rows=10 verified")

    return checks


def has_safety_boundary(text: str) -> bool:
    normalized = text.lower()
    return (
        ("closed simulation" in normalized or "simulated effect" in normalized)
        and "no rf" in normalized
        and ("no exploit" in normalized or "no real packet" in normalized)
    )


def check_zip() -> list[str]:
    require(ZIP_PATH.exists(), f"missing package ZIP: {ZIP_PATH.relative_to(ROOT)}")
    require(MANIFEST_PATH.exists(), f"missing package manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = set(zf.namelist())
    for rel in ZIP_REQUIRED_FILES:
        require(rel in names, f"package ZIP missing {rel}")

    excluded_checks: dict[str, Callable[[str], bool]] = {
        "__pycache__": lambda name: "__pycache__" in name,
        "*.pyc": lambda name: name.endswith(".pyc"),
        "outputs/tmp*": lambda name: name.startswith("outputs/tmp"),
        "outputs/datasets/": lambda name: name.startswith("outputs/datasets/"),
        "*.pkl": lambda name: name.endswith(".pkl"),
        "*.pt": lambda name: name.endswith(".pt"),
        "outputs/batch/seed_*": lambda name: name.startswith("outputs/batch/seed_"),
    }
    for label, predicate in excluded_checks.items():
        hits = [name for name in names if predicate(name)]
        require(not hits, f"package ZIP contains excluded {label}: {hits[:3]}")

    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    require("zip_sha256" in manifest_text, "manifest missing zip_sha256")
    require("outputs/report_tables/battle_timeline.md" in manifest_text, "manifest missing battle timeline")
    require("outputs/report_tables/incident_summary.md" in manifest_text, "manifest missing incident summary")
    require(
        "outputs/report_tables/competition_alignment_matrix.md" in manifest_text,
        "manifest missing competition alignment matrix",
    )
    require(
        "outputs/report_tables/agent_contract_validation.md" in manifest_text,
        "manifest missing agent contract validation",
    )
    require(
        "outputs/report_tables/decision_trace_quality_audit.md" in manifest_text,
        "manifest missing decision trace quality audit",
    )
    return [f"package_zip entries={len(names)}", "package exclusions=passed"]


def check_git_state(require_clean: bool) -> list[str]:
    checks = []
    branch = run(["git", "branch", "--show-current"])
    require(branch == "hbin", f"expected branch hbin, got {branch}")
    checks.append("branch=hbin")

    refs = run(["git", "ls-remote", "--heads", "origin", "main", "hbin"])
    require("refs/heads/main" in refs, "origin/main is missing")
    require("refs/heads/hbin" in refs, "origin/hbin is missing")
    checks.append("origin main/hbin refs=present")

    if require_clean:
        status = run(["git", "status", "--short"])
        tracked_dirty = [
            line
            for line in status.splitlines()
            if line and not line.startswith("?? ") and "outputs/package/DAH2026_source_LIG_DAH_AGI.zip" not in line
        ]
        require(not tracked_dirty, f"tracked working tree is dirty: {tracked_dirty[:8]}")
        checks.append("tracked_worktree=clean")
    return checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify final DAH submission state.")
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Fail when tracked files have uncommitted changes.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checks = []
    checks.extend(check_required_files())
    checks.extend(check_csv_outputs())
    checks.extend(check_zip())
    checks.extend(check_git_state(require_clean=args.require_clean))
    print("Submission state verification passed")
    for item in checks:
        print(f"- {item}")


if __name__ == "__main__":
    main()
