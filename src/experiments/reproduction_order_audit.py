from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/reproduction_order_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/reproduction_order_audit.md"

SAFETY_BOUNDARY = (
    "closed simulation reproduction-order audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "check_id",
    "command",
    "command_index",
    "required_before",
    "order_status",
    "output_files",
    "output_status",
    "status",
    "interpretation",
    "safety_boundary",
]


@dataclass(frozen=True)
class OrderSpec:
    check_id: str
    command: str
    required_before: tuple[str, ...]
    output_files: tuple[str, ...]
    interpretation: str


SPECS = [
    OrderSpec(
        check_id="RO01",
        command="python3 -m src.experiments.defense_action_attribution_audit --fail-on-error",
        required_before=(
            "python3 -m src.experiments.defense_effectiveness_ledger",
            "python3 -m src.experiments.run_tsra_ablation",
            "python3 -m src.experiments.reactive_defense_tradeoff_audit --fail-on-error",
        ),
        output_files=(
            "outputs/report_tables/defense_action_attribution_audit.csv",
            "outputs/report_tables/defense_action_attribution_audit.md",
        ),
        interpretation=(
            "Defense attribution needs event-level ledger evidence, ablation evidence, and "
            "reactive-window evidence before it can classify all TSRA-R actions."
        ),
    ),
    OrderSpec(
        check_id="RO02",
        command="python3 -m src.experiments.closed_loop_episode_replay",
        required_before=(
            "python3 -m src.experiments.attack_defense_response_audit",
            "python3 -m src.experiments.operator_alerts",
            "python3 -m src.experiments.defense_effectiveness_ledger",
        ),
        output_files=(
            "outputs/report_tables/closed_loop_episode_replay.csv",
            "outputs/report_tables/closed_loop_episode_replay.md",
        ),
        interpretation=(
            "Closed-loop replay must run after response coverage, operator alert, and defense "
            "effectiveness evidence exist."
        ),
    ),
    OrderSpec(
        check_id="RO03",
        command="python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error",
        required_before=(
            "python3 -m src.experiments.attack_defense_response_audit",
            "python3 -m src.experiments.closed_loop_episode_replay",
            "python3 -m src.experiments.operator_alerts",
        ),
        output_files=(
            "outputs/report_tables/agent_coordination_latency_audit.csv",
            "outputs/report_tables/agent_coordination_latency_audit.md",
        ),
        interpretation=(
            "Coordination latency is only meaningful after episode replay and response evidence "
            "have been regenerated."
        ),
    ),
    OrderSpec(
        check_id="RO04",
        command="python3 -m src.experiments.agent_engagement_scorecard",
        required_before=(
            "python3 -m src.experiments.closed_loop_episode_replay",
            "python3 -m src.experiments.agent_decision_margin_audit",
            "python3 -m src.experiments.defense_effectiveness_ledger",
        ),
        output_files=(
            "outputs/report_tables/agent_engagement_scorecard.csv",
            "outputs/report_tables/agent_engagement_scorecard.md",
        ),
        interpretation=(
            "The engagement scorecard joins closed-loop episodes, attack decision margins, and "
            "defense-event metric movement."
        ),
    ),
    OrderSpec(
        check_id="RO05",
        command="python3 -m src.experiments.mission_thread_summary --fail-on-error",
        required_before=(
            "python3 -m src.experiments.closed_loop_episode_replay",
            "python3 -m src.experiments.agent_engagement_scorecard",
            "python3 -m src.experiments.defense_action_attribution_audit --fail-on-error",
        ),
        output_files=(
            "outputs/report_tables/mission_thread_summary.csv",
            "outputs/report_tables/mission_thread_summary.md",
        ),
        interpretation=(
            "Mission threads should be generated only after replay, scorecard, and action "
            "attribution are fresh."
        ),
    ),
    OrderSpec(
        check_id="RO06",
        command="python3 -m src.experiments.cross_agent_context_audit --fail-on-error",
        required_before=(
            "python3 -m src.experiments.run_all",
        ),
        output_files=(
            "outputs/report_tables/cross_agent_context_audit.csv",
            "outputs/report_tables/cross_agent_context_audit.md",
        ),
        interpretation=(
            "Cross-agent context audit should run after core traces are fresh "
            "so AURA defense context and TSRA-R attack context can be verified."
        ),
    ),
    OrderSpec(
        check_id="RO07",
        command="python3 -m src.experiments.aura_attack_decision_path_audit --fail-on-error",
        required_before=(
            "python3 -m src.experiments.run_all",
            "python3 -m src.experiments.cross_agent_context_audit --fail-on-error",
        ),
        output_files=(
            "outputs/report_tables/aura_attack_decision_path_audit.csv",
            "outputs/report_tables/aura_attack_decision_path_audit.md",
        ),
        interpretation=(
            "AURA attack path audit should run after core AURA traces and cross-agent context "
            "evidence are fresh so candidate scoring, event links, and defense-context score terms can be checked."
        ),
    ),
    OrderSpec(
        check_id="RO08",
        command="python3 -m src.experiments.defense_priority_decision_path_audit --fail-on-error",
        required_before=(
            "python3 -m src.experiments.run_all",
            "python3 -m src.experiments.cross_agent_context_audit --fail-on-error",
        ),
        output_files=(
            "outputs/report_tables/defense_priority_decision_path_audit.csv",
            "outputs/report_tables/defense_priority_decision_path_audit.md",
        ),
        interpretation=(
            "Defense priority path audit should run after core TSRA-R traces and cross-agent "
            "context evidence are fresh so attack-context priority scores can be checked."
        ),
    ),
    OrderSpec(
        check_id="RO09",
        command="python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error",
        required_before=(
            "python3 -m src.experiments.agent_engagement_scorecard",
        ),
        output_files=(
            "outputs/report_tables/ml_attack_decision_path_audit.csv",
            "outputs/report_tables/ml_attack_decision_path_audit.md",
        ),
        interpretation=(
            "The ML attack path audit uses engagement scorecard feedback to close the AURA-ML "
            "selection loop."
        ),
    ),
    OrderSpec(
        check_id="RO10",
        command="python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error",
        required_before=(
            "python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error",
        ),
        output_files=(
            "outputs/report_tables/ml_defense_decision_path_audit.csv",
            "outputs/report_tables/ml_defense_decision_path_audit.md",
        ),
        interpretation=(
            "The ML defense path audit uses coordination latency evidence to prove closed-loop "
            "response effect."
        ),
    ),
    OrderSpec(
        check_id="RO11",
        command="python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error",
        required_before=(
            "python3 -m src.experiments.ml_attack_decision_path_audit --fail-on-error",
            "python3 -m src.experiments.ml_defense_decision_path_audit --fail-on-error",
            "python3 -m src.experiments.agent_coordination_latency_audit --fail-on-error",
        ),
        output_files=(
            "outputs/report_tables/ml_red_blue_interaction_audit.csv",
            "outputs/report_tables/ml_red_blue_interaction_audit.md",
        ),
        interpretation=(
            "The red-blue interaction audit should run after both ML path audits and the shared "
            "coordination evidence exist."
        ),
    ),
    OrderSpec(
        check_id="RO12",
        command="python3 -m src.experiments.adaptive_defense_decision_path_audit --fail-on-error",
        required_before=(
            "python3 -m src.experiments.run_adaptive_memory",
        ),
        output_files=(
            "outputs/report_tables/adaptive_defense_decision_path_audit.csv",
            "outputs/report_tables/adaptive_defense_decision_path_audit.md",
        ),
        interpretation=(
            "The adaptive defense path audit reads adaptive-memory trace outputs, so it must run "
            "after the adaptive memory comparison regenerates those traces."
        ),
    ),
    OrderSpec(
        check_id="RO13",
        command="python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error",
        required_before=(
            "python3 -m src.ml.train_tsra_detector --rows 5000",
            "python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error",
            "python3 -m src.experiments.attack_defense_response_audit",
        ),
        output_files=(
            "outputs/report_tables/agent_stress_scenario_audit.csv",
            "outputs/report_tables/agent_stress_scenario_audit.md",
        ),
        interpretation=(
            "Stress scenario audit should run after detector training, response evidence, and "
            "the ML red-blue interaction audit so robustness evidence is generated before final gates."
        ),
    ),
    OrderSpec(
        check_id="RO14",
        command="python3 -m src.experiments.competition_alignment --fail-on-incomplete",
        required_before=(
            "python3 -m src.experiments.agent_collaboration_graph",
            "python3 -m src.experiments.ml_red_blue_interaction_audit --fail-on-error",
            "python3 -m src.experiments.agent_stress_scenario_audit --fail-on-error",
            "python3 -m src.experiments.reproduction_order_audit --fail-on-error",
        ),
        output_files=(
            "outputs/report_tables/competition_alignment_matrix.csv",
            "outputs/report_tables/competition_alignment_matrix.md",
        ),
        interpretation=(
            "Competition alignment should be the final evidence matrix after the graph, ML "
            "interaction, and reproduction-order checks are generated."
        ),
    ),
    OrderSpec(
        check_id="RO15",
        command="python3 scripts/build_submission_package.py",
        required_before=(
            "python3 -m src.experiments.submission_readiness_audit --fail-on-incomplete",
            "python3 -m src.experiments.competition_alignment --fail-on-incomplete",
        ),
        output_files=(
            "outputs/package/submission_manifest.md",
        ),
        interpretation=(
            "The package should be built only after readiness and alignment evidence have been "
            "regenerated."
        ),
    ),
    OrderSpec(
        check_id="RO16",
        command="python3 scripts/generate_release_handoff.py",
        required_before=(
            "python3 scripts/build_submission_package.py",
        ),
        output_files=(
            "outputs/package/release_handoff.md",
        ),
        interpretation=(
            "The handoff records package metadata, so it must run after package generation."
        ),
    ),
    OrderSpec(
        check_id="RO17",
        command="python3 scripts/verify_submission_state.py",
        required_before=(
            "python3 scripts/freeze_release_candidate.py",
        ),
        output_files=(),
        interpretation=(
            "Final verification should follow the freeze command so manifest, handoff, package, "
            "and link self-test evidence are current."
        ),
    ),
]


def readme_commands(readme_path: Path = ROOT / "README.md") -> list[str]:
    text = readme_path.read_text(encoding="utf-8")
    marker = "## Full Reproduction"
    if marker not in text:
        return []
    section = text.split(marker, 1)[1]
    match = re.search(r"```bash\n(.*?)\n```", section, flags=re.DOTALL)
    if not match:
        return []
    commands = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            commands.append(line)
    return commands


def command_index(commands: list[str], command: str) -> int | None:
    try:
        return commands.index(command)
    except ValueError:
        return None


def collect_rows(commands: list[str] | None = None) -> list[dict[str, str]]:
    commands = readme_commands() if commands is None else commands
    rows = []
    for spec in SPECS:
        current_index = command_index(commands, spec.command)
        missing_required = []
        late_required = []
        for required in spec.required_before:
            required_index = command_index(commands, required)
            if required_index is None:
                missing_required.append(required)
            elif current_index is None or required_index >= current_index:
                late_required.append(required)
        missing_outputs = [
            rel
            for rel in spec.output_files
            if not (ROOT / rel).exists() or (ROOT / rel).stat().st_size == 0
        ]
        if current_index is None:
            order_status = "missing_command"
        elif missing_required:
            order_status = "missing_prerequisite_command"
        elif late_required:
            order_status = "prerequisite_after_command"
        else:
            order_status = "pass"
        output_status = "pass" if not missing_outputs else "missing_output"
        status = "pass" if order_status == "pass" and output_status == "pass" else "fail"
        rows.append(
            {
                "check_id": spec.check_id,
                "command": spec.command,
                "command_index": "" if current_index is None else str(current_index + 1),
                "required_before": " | ".join(spec.required_before) or "none",
                "order_status": order_status,
                "output_files": " | ".join(spec.output_files) or "not_applicable",
                "output_status": output_status,
                "status": status,
                "interpretation": render_interpretation(
                    spec=spec,
                    missing_required=missing_required,
                    late_required=late_required,
                    missing_outputs=missing_outputs,
                ),
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return rows


def render_interpretation(
    *,
    spec: OrderSpec,
    missing_required: list[str],
    late_required: list[str],
    missing_outputs: list[str],
) -> str:
    issues = []
    if missing_required:
        issues.append("missing prerequisites: " + ", ".join(missing_required))
    if late_required:
        issues.append("late prerequisites: " + ", ".join(late_required))
    if missing_outputs:
        issues.append("missing outputs: " + ", ".join(missing_outputs))
    if issues:
        return spec.interpretation + " Issues: " + "; ".join(issues)
    return spec.interpretation


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Reproduction Order Audit",
        "",
        "This audit checks that README Full Reproduction commands are ordered so generated evidence does not depend on stale downstream files.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'status'))}",
        "",
        "| check_id | command_index | command | order_status | output_status | status |",
        "|---|---:|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["check_id"]),
                    row["command_index"],
                    md(row["command"]),
                    md(row["order_status"]),
                    md(row["output_status"]),
                    md(row["status"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['check_id']}",
                "",
                f"- Command: `{row['command']}`",
                f"- Required before: {row['required_before']}",
                f"- Output files: {row['output_files']}",
                f"- Order status: {row['order_status']}",
                f"- Output status: {row['output_status']}",
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
    parser = argparse.ArgumentParser(description="Audit README Full Reproduction command ordering.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any reproduction-order row fails.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    args = parse_args()
    rows = collect_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["status"] != "pass"]
    print(f"Wrote {display_path(args.output_csv)} ({len(rows)} rows)")
    print(f"Wrote {display_path(args.output_md)} ({len(rows)} rows)")
    if failed:
        print(
            "Failed reproduction-order rows: "
            + ", ".join(row["check_id"] for row in failed)
        )
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
