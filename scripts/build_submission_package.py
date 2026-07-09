from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "outputs" / "package"
DEFAULT_ZIP = PACKAGE_DIR / "DAH2026_소스코드_LIG_DAH_AGI.zip"
MANIFEST_PATH = PACKAGE_DIR / "submission_manifest.md"
ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)

ROOT_FILES = [
    "README.md",
    "requirements.txt",
    "requirements-gpu.txt",
    ".gitignore",
    ".github/workflows/quality.yml",
]

REQUIRED_PATHS = [
    "README.md",
    "requirements.txt",
    "scripts/build_submission_package.py",
    "scripts/freeze_release_candidate.py",
    "scripts/generate_release_handoff.py",
    "scripts/verify_submission_state.py",
    "scripts/verify_external_package_link.py",
    ".github/workflows/quality.yml",
    "tests/test_agent_regression.py",
    "src/agents/runtime.py",
    "src/aura/rule_decision_engine.py",
    "src/tsra_r/rule_defender.py",
    "src/tsra_r/adaptive_defender.py",
    "src/experiments/aura_attack_decision_path_audit.py",
    "src/experiments/cross_agent_context_audit.py",
    "src/experiments/defense_priority_decision_path_audit.py",
    "src/simulator/mission_simulator.py",
    "src/experiments/run_all.py",
    "src/experiments/run_batch.py",
    "src/experiments/run_adaptive_memory.py",
    "src/experiments/adaptive_defense_decision_path_audit.py",
    "src/experiments/run_ml_threshold_sweep.py",
    "src/experiments/battle_timeline.py",
    "src/experiments/incident_summary.py",
    "src/experiments/operator_alerts.py",
    "src/experiments/defense_effectiveness_ledger.py",
    "src/experiments/defense_action_attribution_audit.py",
    "src/experiments/closed_loop_episode_replay.py",
    "src/experiments/agent_coordination_latency_audit.py",
    "src/experiments/agent_stress_scenario_audit.py",
    "src/experiments/mission_thread_summary.py",
    "src/experiments/agent_engagement_scorecard.py",
    "src/experiments/agent_collaboration_graph.py",
    "src/experiments/competition_alignment.py",
    "src/experiments/validate_event_contracts.py",
    "src/experiments/trace_quality_audit.py",
    "src/experiments/agent_quality_gate_audit.py",
    "src/experiments/team_handoff_audit.py",
    "src/experiments/agent_runtime_invariant_audit.py",
    "src/experiments/agent_loop_replay.py",
    "src/experiments/agent_decision_causality_audit.py",
    "src/experiments/agent_decision_margin_audit.py",
    "src/experiments/agent_goal_alignment_audit.py",
    "src/experiments/agent_decision_feedback_audit.py",
    "src/experiments/agent_memory_belief_audit.py",
    "src/experiments/agent_memory_influence_audit.py",
    "src/experiments/agent_tool_usage_audit.py",
    "src/experiments/agent_interface_manifest.py",
    "src/experiments/agent_capability_matrix.py",
    "src/experiments/attack_defense_coverage.py",
    "src/experiments/attack_defense_response_audit.py",
    "src/experiments/pace_transition_audit.py",
    "src/experiments/mission_impact_decomposition.py",
    "src/experiments/metric_gate.py",
    "src/experiments/ml_contribution_audit.py",
    "src/experiments/ml_attack_decision_path_audit.py",
    "src/experiments/ml_defense_decision_path_audit.py",
    "src/experiments/ml_red_blue_interaction_audit.py",
    "src/experiments/reactive_defense_tradeoff_audit.py",
    "src/experiments/tsra_detector_calibration_audit.py",
    "src/experiments/safety_boundary_audit.py",
    "src/experiments/reproduction_order_audit.py",
    "src/experiments/submission_readiness_audit.py",
    "docs/process/COMPETITION_DIRECTION.md",
    "docs/process/NEXT_DEVELOPMENT_QUEUE.md",
    "docs/process/DEVELOPMENT_LOG.md",
    "docs/process/FINAL_QA.md",
    "docs/process/SUBMISSION_PACKAGE.md",
    "docs/process/TEAM_HANDOFF.md",
    "docs/agents/AGENT_RUNTIME.md",
    "docs/agents/AURA_ATTACK_AGENT.md",
    "docs/agents/TSRA_R_DEFENSE_AGENT.md",
    "outputs/experiments/experiment_summary.csv",
    "outputs/batch/repeated_experiment_summary.csv",
    "outputs/batch/resilience_gain_summary.csv",
    "outputs/batch/tsra_action_ablation_summary.csv",
    "outputs/batch/adaptive_memory_summary.csv",
    "outputs/report_tables/cross_agent_context_audit.md",
    "outputs/report_tables/defense_priority_decision_path_audit.md",
    "outputs/report_tables/adaptive_defense_decision_path_audit.md",
    "outputs/batch/ml_threshold_sweep_summary.csv",
    "outputs/figures/aura_tsra_architecture.png",
    "outputs/figures/batch_resilience_gain.png",
    "outputs/figures/tsra_action_ablation.png",
    "outputs/figures/adaptive_memory_comparison.png",
    "outputs/report_tables/agent_decision_trace_summary.md",
    "outputs/report_tables/battle_timeline.md",
    "outputs/report_tables/incident_summary.md",
    "outputs/report_tables/operator_alerts.md",
    "outputs/report_tables/defense_effectiveness_ledger.md",
    "outputs/report_tables/defense_action_attribution_audit.md",
    "outputs/report_tables/closed_loop_episode_replay.md",
    "outputs/report_tables/agent_coordination_latency_audit.md",
    "outputs/report_tables/agent_stress_scenario_audit.md",
    "outputs/report_tables/mission_thread_summary.md",
    "outputs/report_tables/agent_engagement_scorecard.md",
    "outputs/report_tables/agent_collaboration_graph.md",
    "outputs/report_tables/agent_collaboration_graph.mmd",
    "outputs/report_tables/competition_alignment_matrix.md",
    "outputs/report_tables/agent_contract_validation.md",
    "outputs/report_tables/decision_trace_quality_audit.md",
    "outputs/report_tables/agent_quality_gate_audit.csv",
    "outputs/report_tables/agent_quality_gate_audit.md",
    "outputs/report_tables/team_handoff_audit.csv",
    "outputs/report_tables/team_handoff_audit.md",
    "outputs/report_tables/agent_runtime_invariant_audit.md",
    "outputs/report_tables/agent_loop_replay.md",
    "outputs/report_tables/agent_decision_causality_audit.md",
    "outputs/report_tables/agent_decision_margin_audit.md",
    "outputs/report_tables/agent_goal_alignment_audit.md",
    "outputs/report_tables/agent_decision_feedback_audit.md",
    "outputs/report_tables/agent_memory_belief_audit.md",
    "outputs/report_tables/agent_memory_influence_audit.md",
    "outputs/report_tables/aura_attack_decision_path_audit.md",
    "outputs/report_tables/agent_tool_usage_audit.md",
    "outputs/report_tables/agent_interface_manifest.md",
    "outputs/report_tables/agent_capability_matrix.md",
    "outputs/report_tables/attack_defense_coverage.md",
    "outputs/report_tables/attack_defense_response_audit.md",
    "outputs/report_tables/pace_transition_audit.md",
    "outputs/report_tables/mission_impact_decomposition.md",
    "outputs/report_tables/metric_gate_summary.md",
    "outputs/report_tables/ml_contribution_audit.md",
    "outputs/report_tables/ml_attack_decision_path_audit.md",
    "outputs/report_tables/ml_defense_decision_path_audit.md",
    "outputs/report_tables/ml_red_blue_interaction_audit.md",
    "outputs/report_tables/reactive_defense_tradeoff_audit.md",
    "outputs/report_tables/ml_threshold_sweep.md",
    "outputs/report_tables/tsra_detector_calibration_audit.md",
    "outputs/report_tables/tsra_detector_calibration_bins.csv",
    "outputs/report_tables/safety_boundary_audit.md",
    "outputs/report_tables/reproduction_order_audit.md",
    "outputs/report_tables/submission_readiness_audit.md",
    "outputs/report_tables/aura_coa_cards.md",
    "outputs/models/aura_impact_model_metrics.json",
    "outputs/models/tsra_detector_metrics.json",
    "outputs/models/aura_mps_mlp_metrics.json",
]

EXCLUDED_PREFIXES = [
    ".git/",
    ".venv",
    "outputs/batch/seed_",
    "outputs/datasets/",
    "outputs/tmp",
]

EXCLUDED_PARTS = {
    "__pycache__",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pkl",
    ".pt",
    ".DS_Store",
}


def is_excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return True
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return True
    return any(rel.endswith(suffix) for suffix in EXCLUDED_SUFFIXES)


def collect_files() -> list[Path]:
    files: set[Path] = set()

    for rel in ROOT_FILES:
        path = ROOT / rel
        if path.exists() and not is_excluded(path):
            files.add(path)

    for folder in ["src", "docs", "scripts", "tests", ".github"]:
        root = ROOT / folder
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and not is_excluded(path):
                files.add(path)

    curated_outputs = [
        ROOT / "outputs" / "experiments" / "experiment_summary.csv",
        ROOT / "outputs" / "batch",
        ROOT / "outputs" / "figures",
        ROOT / "outputs" / "models",
        ROOT / "outputs" / "report_tables",
    ]
    for item in curated_outputs:
        if not item.exists():
            continue
        if item.is_file() and not is_excluded(item):
            files.add(item)
            continue
        for path in item.rglob("*"):
            if path.is_file() and not is_excluded(path):
                files.add(path)

    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def validate_required(files: list[Path]) -> list[str]:
    rels = {path.relative_to(ROOT).as_posix() for path in files}
    missing = [rel for rel in REQUIRED_PATHS if rel not in rels]
    return missing


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(files: list[Path], zip_path: Path | None = None) -> Path:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    total_bytes = sum(path.stat().st_size for path in files)
    lines = [
        "# 제출 패키지 Manifest",
        "",
        "이 manifest는 `scripts/build_submission_package.py`로 생성한다.",
        "",
        "## 포함 기준",
        "",
        "- `README.md`, `requirements*.txt`",
        "- `.github/workflows/quality.yml`: hbin branch quality gate",
        "- `src/`: 공격/방어 에이전트, 시뮬레이터, ML, 실험 코드",
        "- `tests/`: agent runtime, AURA-ML, TSRA-R regression tests",
        "- `docs/`: 시나리오, 에이전트, 개발 판단 근거",
        "- `outputs/batch/*.csv`: 반복 실험과 ablation/adaptive 요약",
        "- `outputs/figures/*.png`: 핵심 그래프와 아키텍처 그림",
        "- `outputs/report_tables/*`: trace/COA/readiness/ML contribution/closed-loop mission thread 요약표",
        "- `outputs/models/*_metrics.json`: 모델 성능 메트릭",
        "",
        "## 제외 기준",
        "",
        "- `.git/`, `.venv*`, `__pycache__/`, `*.pyc`",
        "- `outputs/tmp*`: 재생성 가능한 임시 실행 로그",
        "- `outputs/batch/seed_*`: 30-seed 실행 중간 로그",
        "- `outputs/datasets/`: 재생성 가능한 synthetic dataset",
        "- `outputs/models/*.pkl`, `outputs/models/*.pt`: 재생성 가능한 model binary",
        "",
        "## 패키지 요약",
        "",
        f"- payload_file_count: {len(files)}",
        f"- total_payload_bytes: {total_bytes}",
    ]
    if zip_path and zip_path.exists():
        lines.extend(
            [
                f"- zip_path: `{zip_path.relative_to(ROOT).as_posix()}`",
                f"- zip_file_count: {len(files) + 1}",
                f"- zip_bytes: {zip_path.stat().st_size}",
                f"- zip_sha256: `{sha256_file(zip_path)}`",
            ]
        )
    lines.extend(["", "## 포함 파일", ""])
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        lines.append(f"- `{rel}`")
    MANIFEST_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return MANIFEST_PATH


def build_zip(files: list[Path], output: Path) -> Path:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = write_manifest(files)
    package_files = sorted(
        files + [manifest],
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in package_files:
            rel = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(rel, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
            zf.writestr(info, path.read_bytes())
    write_manifest(files, output)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the DAH source package ZIP.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ZIP,
        help="ZIP output path. Defaults to outputs/package/DAH2026_소스코드_LIG_DAH_AGI.zip",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Write only outputs/package/submission_manifest.md without creating a ZIP.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = collect_files()
    missing = validate_required(files)
    if missing:
        missing_list = "\n".join(f"- {rel}" for rel in missing)
        raise SystemExit(f"Required package files are missing:\n{missing_list}")

    if args.manifest_only:
        manifest = write_manifest(files)
        print(f"Wrote {manifest.relative_to(ROOT)}")
        print(f"payload_file_count={len(files)}")
        return

    output = args.output
    if not output.is_absolute():
        output = ROOT / output
    zip_path = build_zip(files, output)
    print(f"Wrote {zip_path.relative_to(ROOT)}")
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"payload_file_count={len(files)}")
    print(f"zip_file_count={len(files) + 1}")
    print(f"zip_bytes={zip_path.stat().st_size}")
    print(f"zip_sha256={sha256_file(zip_path)}")


if __name__ == "__main__":
    main()
