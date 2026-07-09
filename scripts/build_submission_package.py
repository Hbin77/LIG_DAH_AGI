from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "outputs" / "package"
DEFAULT_ZIP = PACKAGE_DIR / "DAH2026_source_LIG_DAH_AGI.zip"
MANIFEST_PATH = PACKAGE_DIR / "submission_manifest.md"

ROOT_FILES = [
    "README.md",
    "requirements.txt",
    "requirements-gpu.txt",
    ".gitignore",
]

REQUIRED_PATHS = [
    "README.md",
    "requirements.txt",
    "scripts/build_submission_package.py",
    "scripts/verify_submission_state.py",
    "src/agents/runtime.py",
    "src/aura/rule_decision_engine.py",
    "src/tsra_r/rule_defender.py",
    "src/tsra_r/adaptive_defender.py",
    "src/simulator/mission_simulator.py",
    "src/experiments/run_all.py",
    "src/experiments/run_batch.py",
    "src/experiments/run_adaptive_memory.py",
    "src/experiments/battle_timeline.py",
    "src/experiments/incident_summary.py",
    "src/experiments/competition_alignment.py",
    "src/experiments/validate_event_contracts.py",
    "docs/process/COMPETITION_DIRECTION.md",
    "docs/process/NEXT_DEVELOPMENT_QUEUE.md",
    "docs/process/DEVELOPMENT_LOG.md",
    "docs/process/FINAL_QA.md",
    "docs/process/SUBMISSION_PACKAGE.md",
    "docs/agents/AGENT_RUNTIME.md",
    "docs/agents/AURA_ATTACK_AGENT.md",
    "docs/agents/TSRA_R_DEFENSE_AGENT.md",
    "outputs/experiments/experiment_summary.csv",
    "outputs/batch/repeated_experiment_summary.csv",
    "outputs/batch/resilience_gain_summary.csv",
    "outputs/batch/tsra_action_ablation_summary.csv",
    "outputs/batch/adaptive_memory_summary.csv",
    "outputs/figures/aura_tsra_architecture.png",
    "outputs/figures/batch_resilience_gain.png",
    "outputs/figures/tsra_action_ablation.png",
    "outputs/figures/adaptive_memory_comparison.png",
    "outputs/report_tables/agent_decision_trace_summary.md",
    "outputs/report_tables/battle_timeline.md",
    "outputs/report_tables/incident_summary.md",
    "outputs/report_tables/competition_alignment_matrix.md",
    "outputs/report_tables/agent_contract_validation.md",
    "outputs/report_tables/aura_coa_cards.md",
    "outputs/models/aura_impact_model_metrics.json",
    "outputs/models/tsra_detector_metrics.json",
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

    for folder in ["src", "docs", "scripts"]:
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
        "- `src/`: 공격/방어 에이전트, 시뮬레이터, ML, 실험 코드",
        "- `docs/`: 시나리오, 에이전트, 개발 판단 근거",
        "- `outputs/batch/*.csv`: 반복 실험과 ablation/adaptive 요약",
        "- `outputs/figures/*.png`: 핵심 그래프와 아키텍처 그림",
        "- `outputs/report_tables/*`: trace/COA/모델 비교 요약표",
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
            zf.write(path, arcname=rel)
    write_manifest(files, output)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the DAH source package ZIP.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ZIP,
        help="ZIP output path. Defaults to outputs/package/DAH2026_source_LIG_DAH_AGI.zip",
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
