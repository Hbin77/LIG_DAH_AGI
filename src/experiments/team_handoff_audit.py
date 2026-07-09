from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/team_handoff_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/team_handoff_audit.md"

SAFETY_BOUNDARY = (
    "closed simulation team-handoff audit only; no RF, exploit, or live network action"
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


def read_text(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def missing_tokens(text: str, tokens: set[str]) -> list[str]:
    return sorted(token for token in tokens if token not in text)


def collect_checks() -> list[dict[str, str]]:
    handoff_path = ROOT / "docs/process/TEAM_HANDOFF.md"
    handoff = read_text("docs/process/TEAM_HANDOFF.md")
    readme = read_text("README.md")
    verifier = read_text("scripts/verify_submission_state.py")
    package_builder = read_text("scripts/build_submission_package.py")
    readiness = read_text("src/experiments/submission_readiness_audit.py")
    alignment = read_text("src/experiments/competition_alignment.py")

    rows: list[dict[str, str]] = []

    required_sections = {
        "## Branch Rule",
        "## Role Lanes",
        "## Change Contract",
        "## Minimum Gate Before Push",
        "## Decision Record Rule",
        "## Safety Boundary",
        "## Handoff Checklist",
    }
    missing_sections = missing_tokens(handoff, required_sections)
    rows.append(
        Check(
            check_id="TH01",
            area="handoff_document_structure",
            requirement="Team handoff guide must exist and contain branch, role, gate, decision, safety, and checklist sections.",
            observed=(
                f"file_exists={str(handoff_path.exists()).lower()}; "
                f"missing_sections={','.join(missing_sections) or 'none'}"
            ),
            status="pass" if handoff_path.exists() and not missing_sections else "fail",
            evidence_files="docs/process/TEAM_HANDOFF.md",
            interpretation="The team handoff guide has enough structure for a new teammate to find the workflow quickly.",
        ).row()
    )

    role_tokens = {
        "Attack agent",
        "Defense agent",
        "ML and metrics",
        "QA and packaging",
        "Integration",
        "src/aura/",
        "src/tsra_r/",
        "src/ml/",
        "tests/",
        "scripts/verify_submission_state.py",
    }
    missing_role_tokens = missing_tokens(handoff, role_tokens)
    rows.append(
        Check(
            check_id="TH02",
            area="role_lane_contract",
            requirement="Handoff guide must split attack, defense, ML, QA, and integration lanes with primary files.",
            observed=f"missing_role_tokens={','.join(missing_role_tokens) or 'none'}",
            status="pass" if not missing_role_tokens else "fail",
            evidence_files="docs/process/TEAM_HANDOFF.md",
            interpretation="Attack and defense development can be assigned separately without guessing file ownership.",
        ).row()
    )

    branch_tokens = {
        "Active development branch: `hbin`",
        "Protected/default branch: `main`",
        "git ls-remote --heads origin main hbin",
        "main` is preserved",
    }
    missing_branch_tokens = missing_tokens(handoff, branch_tokens)
    rows.append(
        Check(
            check_id="TH03",
            area="branch_policy",
            requirement="Handoff guide must preserve hbin as the shared work branch and main as protected/default.",
            observed=f"missing_branch_tokens={','.join(missing_branch_tokens) or 'none'}",
            status="pass" if not missing_branch_tokens else "fail",
            evidence_files="docs/process/TEAM_HANDOFF.md",
            interpretation="The branch policy remains explicit for new teammates and prevents direct main development.",
        ).row()
    )

    gate_tokens = {
        "python3 -m unittest discover -s tests",
        "python3 -m src.experiments.agent_quality_gate_audit --fail-on-error",
        "python3 -m src.experiments.reproduction_order_audit --fail-on-error",
        "python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete",
        "python3 -m src.experiments.competition_alignment --fail-on-incomplete",
        "python3 scripts/freeze_release_candidate.py",
        "python3 scripts/verify_submission_state.py --require-clean",
    }
    missing_gate_tokens = missing_tokens(handoff, gate_tokens)
    rows.append(
        Check(
            check_id="TH04",
            area="minimum_gate_commands",
            requirement="Handoff guide must list the fast checks and final freeze/verification commands.",
            observed=f"missing_gate_tokens={','.join(missing_gate_tokens) or 'none'}",
            status="pass" if not missing_gate_tokens else "fail",
            evidence_files="docs/process/TEAM_HANDOFF.md",
            interpretation="A teammate can run the same quality gates before pushing or handing off work.",
        ).row()
    )

    decision_tokens = {
        "docs/process/DEVELOPMENT_LOG.md",
        "docs/process/NEXT_DEVELOPMENT_QUEUE.md",
        "README Full Reproduction",
        "Regenerate package manifest",
        "release handoff",
    }
    missing_decision_tokens = missing_tokens(handoff, decision_tokens)
    rows.append(
        Check(
            check_id="TH05",
            area="decision_record_contract",
            requirement="Handoff guide must require rationale, queue, reproduction, package, and release-handoff updates.",
            observed=f"missing_decision_tokens={','.join(missing_decision_tokens) or 'none'}",
            status="pass" if not missing_decision_tokens else "fail",
            evidence_files="docs/process/TEAM_HANDOFF.md",
            interpretation="Development rationale remains traceable through docs and generated handoff artifacts.",
        ).row()
    )

    forbidden_phrases = {
        "나 혼자",
        "solo work",
        "one-person",
    }
    missing_integration_tokens = {
        "docs/process/TEAM_HANDOFF.md": "docs/process/TEAM_HANDOFF.md",
        "team_handoff_audit": "team_handoff_audit",
        "team_handoff_audit.csv": "team_handoff_audit.csv",
    }
    integration_sources = "\n".join([readme, verifier, package_builder, readiness, alignment])
    missing_integration = [
        label
        for token, label in missing_integration_tokens.items()
        if token not in integration_sources
    ]
    forbidden_hits = [
        phrase
        for phrase in forbidden_phrases
        if phrase in "\n".join([handoff, readme, readiness])
    ]
    rows.append(
        Check(
            check_id="TH06",
            area="package_and_readiness_integration",
            requirement="Team handoff guide and audit must be connected to README, final verifier, package builder, readiness, and alignment.",
            observed=(
                f"missing_integration={','.join(missing_integration) or 'none'}; "
                f"forbidden_team_phrases={','.join(forbidden_hits) or 'none'}"
            ),
            status="pass" if not missing_integration and not forbidden_hits else "fail",
            evidence_files=(
                "README.md | scripts/verify_submission_state.py | scripts/build_submission_package.py | "
                "src/experiments/submission_readiness_audit.py | src/experiments/competition_alignment.py"
            ),
            interpretation="The handoff guide is part of the verified package workflow and avoids personal-only wording.",
        ).row()
    )

    safety_tokens = {
        "actual RF",
        "exploit",
        "live network action",
        "python3 -m src.experiments.safety_boundary_audit --fail-on-error",
    }
    missing_safety_tokens = missing_tokens(handoff, safety_tokens)
    rows.append(
        Check(
            check_id="TH07",
            area="safety_boundary",
            requirement="Handoff guide must preserve the closed-simulation safety boundary and safety audit command.",
            observed=f"missing_safety_tokens={','.join(missing_safety_tokens) or 'none'}",
            status="pass" if not missing_safety_tokens else "fail",
            evidence_files="docs/process/TEAM_HANDOFF.md",
            interpretation="New teammates receive the safety boundary before touching attack or defense code.",
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
        "# Team Handoff Audit",
        "",
        "This audit verifies that the team handoff guide is structured, role-specific, branch-safe, gate-driven, and integrated into the verified package workflow.",
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
    parser = argparse.ArgumentParser(description="Audit team handoff documentation and integration.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any team-handoff audit row fails.",
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
        print("Failed team-handoff rows: " + ", ".join(row["check_id"] for row in failed))
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
