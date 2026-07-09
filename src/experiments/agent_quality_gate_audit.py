from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/agent_quality_gate_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/agent_quality_gate_audit.md"

SAFETY_BOUNDARY = (
    "closed simulation agent quality-gate audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "check_id",
    "area",
    "requirement",
    "observed",
    "status",
    "evidence_files",
    "interpretation",
    "safety_boundary",
]


@dataclass(frozen=True)
class Check:
    check_id: str
    area: str
    requirement: str
    observed: str
    status: str
    evidence_files: str
    interpretation: str

    def row(self) -> dict[str, str]:
        return {
            "check_id": self.check_id,
            "area": self.area,
            "requirement": self.requirement,
            "observed": self.observed,
            "status": self.status,
            "evidence_files": self.evidence_files,
            "interpretation": self.interpretation,
            "safety_boundary": SAFETY_BOUNDARY,
        }


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def full_reproduction_commands(readme_text: str) -> list[str]:
    marker = "## Full Reproduction"
    if marker not in readme_text:
        return []
    section = readme_text.split(marker, 1)[1]
    match = re.search(r"```bash\n(.*?)\n```", section, flags=re.DOTALL)
    if not match:
        return []
    return [
        line.strip()
        for line in match.group(1).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def command_before(commands: list[str], earlier: str, later: str) -> bool:
    try:
        return commands.index(earlier) < commands.index(later)
    except ValueError:
        return False


def run_unittest() -> tuple[bool, int, str]:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = "\n".join(
        part for part in [result.stdout.strip(), result.stderr.strip()] if part
    )
    match = re.search(r"Ran\s+(\d+)\s+tests?", output)
    test_count = int(match.group(1)) if match else 0
    return result.returncode == 0, test_count, output.replace("\n", " | ")


def collect_checks() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    unittest_ok, test_count, unittest_output = run_unittest()
    rows.append(
        Check(
            check_id="AQG01",
            area="unit_regression_execution",
            requirement="Agent core regression tests must execute locally and pass.",
            observed=f"test_count={test_count}; result={'pass' if unittest_ok else 'fail'}; output={unittest_output}",
            status="pass" if unittest_ok and test_count >= 3 else "fail",
            evidence_files="tests/test_agent_regression.py",
            interpretation=(
                "Fast regression tests run before full experiments, so core agent invariants fail early."
            ),
        ).row()
    )

    test_path = ROOT / "tests/test_agent_regression.py"
    test_text = test_path.read_text(encoding="utf-8") if test_path.exists() else ""
    required_test_tokens = {
        "AgentRuntimeRegressionTests",
        "AuraMLRegressionTests",
        "TsraRRegressionTests",
        "event.agent",
        "AURA-ML",
        "selection_score",
        "defense_priority_score",
        "cooldown",
    }
    missing_test_tokens = sorted(token for token in required_test_tokens if token not in test_text)
    rows.append(
        Check(
            check_id="AQG02",
            area="unit_regression_scope",
            requirement=(
                "Tests must cover AgentRuntime, AURA-ML identity/scoring, and TSRA-R priority/cooldown invariants."
            ),
            observed=f"missing_scope_tokens={','.join(missing_test_tokens) or 'none'}",
            status="pass" if not missing_test_tokens else "fail",
            evidence_files="tests/test_agent_regression.py",
            interpretation=(
                "The test file names the three agent-core regression areas instead of only checking file existence."
            ),
        ).row()
    )

    verifier_text = read_text("scripts/verify_submission_state.py")
    required_verifier_tokens = {
        "check_regression_tests",
        "unittest",
        "discover",
        "-s",
        "tests",
        "agent_regression_tests",
        "tests/test_agent_regression.py",
        ".github/workflows/quality.yml",
    }
    missing_verifier_tokens = sorted(
        token for token in required_verifier_tokens if token not in verifier_text
    )
    rows.append(
        Check(
            check_id="AQG03",
            area="final_verifier_integration",
            requirement="Final verifier must execute agent regression tests and require test/workflow files.",
            observed=f"missing_verifier_tokens={','.join(missing_verifier_tokens) or 'none'}",
            status="pass" if not missing_verifier_tokens else "fail",
            evidence_files="scripts/verify_submission_state.py",
            interpretation=(
                "Regression tests are part of the final gate, not an optional developer command."
            ),
        ).row()
    )

    workflow_text = read_text(".github/workflows/quality.yml")
    workflow_requirements = {
        "branches:": "branch trigger section",
        "- hbin": "hbin-only push trigger",
        "ref: hbin": "explicit hbin checkout",
        "python -m compileall -q src scripts tests": "compile gate",
        "python -m unittest discover -s tests": "unit regression gate",
        "python scripts/build_submission_package.py": "package rebuild gate",
        "python scripts/generate_release_handoff.py": "handoff regeneration gate",
        "python scripts/verify_submission_state.py": "final verifier gate",
    }
    missing_workflow_tokens = [
        description
        for token, description in workflow_requirements.items()
        if token not in workflow_text
    ]
    main_trigger_present = re.search(r"branches:\s*\n\s*-\s*main\b", workflow_text) is not None
    rows.append(
        Check(
            check_id="AQG04",
            area="hbin_workflow_gate",
            requirement="GitHub Actions quality gate must run on hbin and avoid main-branch push automation.",
            observed=(
                f"missing_workflow_tokens={','.join(missing_workflow_tokens) or 'none'}; "
                f"main_branch_trigger={str(main_trigger_present).lower()}"
            ),
            status="pass" if not missing_workflow_tokens and not main_trigger_present else "fail",
            evidence_files=".github/workflows/quality.yml",
            interpretation=(
                "CI protects the shared hbin branch while preserving main as a separate protected branch."
            ),
        ).row()
    )

    readme_text = read_text("README.md")
    commands = full_reproduction_commands(readme_text)
    unittest_command = "python3 -m unittest discover -s tests"
    quality_audit_command = "python3 -m src.experiments.agent_quality_gate_audit --fail-on-error"
    full_repro_ok = (
        unittest_command in commands
        and quality_audit_command in commands
        and command_before(commands, unittest_command, quality_audit_command)
        and command_before(commands, quality_audit_command, "python3 -m src.experiments.run_all")
    )
    rows.append(
        Check(
            check_id="AQG05",
            area="readme_reproduction_gate",
            requirement="README Full Reproduction must run unit regression and this audit before heavy experiments.",
            observed=(
                f"unittest_command_present={str(unittest_command in commands).lower()}; "
                f"quality_audit_command_present={str(quality_audit_command in commands).lower()}; "
                f"quality_before_run_all={str(command_before(commands, quality_audit_command, 'python3 -m src.experiments.run_all')).lower()}"
            ),
            status="pass" if full_repro_ok else "fail",
            evidence_files="README.md",
            interpretation=(
                "The fast code gate appears early in reproduction order, before long-running experiments."
            ),
        ).row()
    )

    package_builder_text = read_text("scripts/build_submission_package.py")
    manifest_text = read_text("outputs/package/submission_manifest.md")
    required_package_tokens = {
        "tests/test_agent_regression.py": "test source",
        ".github/workflows/quality.yml": "quality workflow",
        "tests": "tests folder collector",
        ".github": "workflow folder collector",
    }
    missing_builder_tokens = [
        description
        for token, description in required_package_tokens.items()
        if token not in package_builder_text
    ]
    missing_manifest_tokens = [
        description
        for token, description in required_package_tokens.items()
        if token not in manifest_text
    ]
    rows.append(
        Check(
            check_id="AQG06",
            area="package_inclusion_gate",
            requirement="Submission package must include regression tests and hbin quality workflow.",
            observed=(
                f"missing_builder_tokens={','.join(missing_builder_tokens) or 'none'}; "
                f"missing_manifest_tokens={','.join(missing_manifest_tokens) or 'none'}"
            ),
            status="pass" if not missing_builder_tokens and not missing_manifest_tokens else "fail",
            evidence_files="scripts/build_submission_package.py | outputs/package/submission_manifest.md",
            interpretation=(
                "The regression gate is shipped with the source package and is not only a local workspace artifact."
            ),
        ).row()
    )

    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Quality Gate Audit",
        "",
        "This audit verifies that fast agent-core regression tests and the hbin quality workflow are wired into reproduction, packaging, and final verification.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'status'))}",
        "",
        "| check_id | area | observed | status |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["check_id"]),
                    md(row["area"]),
                    md(row["observed"]),
                    md(row["status"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['check_id']} {row['area']}",
                "",
                f"- Requirement: {row['requirement']}",
                f"- Observed: {row['observed']}",
                f"- Evidence: {row['evidence_files']}",
                f"- Status: {row['status']}",
                f"- Interpretation: {row['interpretation']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def count_values(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = row.get(field, "")
        counts[key] = counts.get(key, 0) + 1
    return counts


def format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit agent regression and hbin quality gates.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any quality-gate audit row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_checks()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["status"] != "pass"]
    print(f"Wrote {rel(args.output_csv)} ({len(rows)} rows)")
    print(f"Wrote {rel(args.output_md)} ({len(rows)} rows)")
    if failed:
        print("Failed quality-gate rows: " + ", ".join(row["check_id"] for row in failed))
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
