from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_contract_validation.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_contract_validation.md")

FIELDNAMES = [
    "experiment",
    "contract",
    "status",
    "checked_rows",
    "required_files",
    "issues",
]

REQUIRED_ATTACK_EVENT_FIELDS = {
    "event_id",
    "selected_at",
    "candidate",
    "expected_impact",
    "reason",
    "score",
    "agent",
}
REQUIRED_ATTACK_CANDIDATE_FIELDS = {
    "attack_type",
    "target_link",
    "target_traffic_classes",
    "start_time",
    "duration_sec",
    "latency_ms_add",
    "jitter_ms_add",
    "packet_loss_add",
    "queue_pressure",
}
REQUIRED_EXPECTED_IMPACT_FIELDS = {
    "mission_impact",
    "p95_critical_latency_sec",
    "stale_data_ratio",
    "priority_inversion_rate",
}
REQUIRED_DEFENSE_EVENT_FIELDS = {"event_id", "time_sec", "action", "details", "agent"}
REQUIRED_METRIC_FIELDS = {
    "time_sec",
    "p95_critical_latency_sec",
    "stale_data_ratio",
    "trusted_stale_exposure",
    "priority_inversion_rate",
    "kill_chain_delay_sec",
    "recovery_instability",
    "mission_impact",
    "delivered_count",
    "dropped_count",
}
REQUIRED_MISSION_EVENT_FIELDS = {"time_sec", "event", "message"}
REQUIRED_MESSAGE_FIELDS = {
    "id",
    "type",
    "source",
    "destination",
    "created_at",
    "size_kb",
    "priority",
    "deadline_sec",
    "route",
    "dropped",
}
REQUIRED_TRACE_FIELDS = {
    "trace_id",
    "agent",
    "time_sec",
    "goal",
    "policy",
    "observation",
    "memory",
    "candidate_actions",
    "tool_calls",
    "selected_action",
    "reason",
    "feedback",
}
REQUIRED_OBSERVATION_FIELDS = {"agent", "time_sec", "mission_phase", "active_link", "signals"}
REQUIRED_OBSERVATION_SIGNAL_FIELDS = {
    "critical_pending",
    "defense_mode",
    "links",
    "priority_inversion_rate",
    "recent_p95_critical_latency_sec",
    "stale_data_ratio",
    "total_queue_kb",
    "video_queue_kb",
}

SIMULATION_SAFETY_TEXT = (
    "closed simulation event-contract validation only; no RF, exploit, or live network action"
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                rows.append({"__decode_error__": f"line {line_number}: {exc}"})
                continue
            rows.append(value)
    return rows


def is_monotonic(rows: list[dict[str, Any]], field: str) -> bool:
    values = [as_float(row.get(field)) for row in rows if field in row]
    return values == sorted(values)


def missing_fields(row: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in row)


def as_float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def validate_experiment(exp_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    rows.append(validate_attack_contract(exp_dir))
    rows.append(validate_defense_contract(exp_dir))
    rows.append(validate_metric_contract(exp_dir))
    rows.append(validate_mission_event_contract(exp_dir))
    rows.append(validate_trace_contract(exp_dir, "aura_decision_traces.jsonl", "AURA"))
    rows.append(validate_trace_contract(exp_dir, "tsra_r_decision_traces.jsonl", "TSRA-R"))
    rows.append(validate_cross_contract(exp_dir))
    return rows


def validate_attack_contract(exp_dir: Path) -> dict[str, str]:
    path = exp_dir / "attack_events.jsonl"
    rows = read_jsonl(path)
    issues = []
    for idx, row in enumerate(rows, start=1):
        issues.extend(prefix(idx, missing_fields(row, REQUIRED_ATTACK_EVENT_FIELDS)))
        candidate = row.get("candidate") or {}
        expected = row.get("expected_impact") or {}
        issues.extend(prefix(idx, missing_fields(candidate, REQUIRED_ATTACK_CANDIDATE_FIELDS), "candidate."))
        if row.get("agent") != "fixed":
            issues.extend(prefix(idx, missing_fields(expected, REQUIRED_EXPECTED_IMPACT_FIELDS), "expected_impact."))
        if row.get("agent") not in {"fixed", "AURA", "AURA-ML"}:
            issues.append(f"row {idx}: unexpected attack agent {row.get('agent')}")
        if as_float(candidate.get("duration_sec")) <= 0:
            issues.append(f"row {idx}: non-positive duration_sec")
        if not isinstance(candidate.get("target_traffic_classes"), list):
            issues.append(f"row {idx}: target_traffic_classes must be a list")
    if rows and not is_monotonic(rows, "selected_at"):
        issues.append("selected_at is not monotonic")
    return result(exp_dir, "attack_event_schema", rows, ["attack_events.jsonl"], issues)


def validate_defense_contract(exp_dir: Path) -> dict[str, str]:
    path = exp_dir / "defense_events.jsonl"
    rows = read_jsonl(path)
    issues = []
    for idx, row in enumerate(rows, start=1):
        issues.extend(prefix(idx, missing_fields(row, REQUIRED_DEFENSE_EVENT_FIELDS)))
        if row.get("agent") not in {"TSRA-R", "TSRA-R-ML", "TSRA-R-ADAPTIVE"}:
            issues.append(f"row {idx}: unexpected defense agent {row.get('agent')}")
        if not isinstance(row.get("details"), dict):
            issues.append(f"row {idx}: details must be an object")
    if rows and not is_monotonic(rows, "time_sec"):
        issues.append("time_sec is not monotonic")
    return result(exp_dir, "defense_event_schema", rows, ["defense_events.jsonl"], issues)


def validate_metric_contract(exp_dir: Path) -> dict[str, str]:
    path = exp_dir / "metric_snapshots.jsonl"
    rows = read_jsonl(path)
    issues = []
    if not rows:
        issues.append("metric_snapshots.jsonl is empty")
    for idx, row in enumerate(rows, start=1):
        issues.extend(prefix(idx, missing_fields(row, REQUIRED_METRIC_FIELDS)))
        for field in REQUIRED_METRIC_FIELDS - {"time_sec", "delivered_count", "dropped_count"}:
            value = as_float(row.get(field))
            if value < 0:
                issues.append(f"row {idx}: negative metric {field}")
    if rows and not is_monotonic(rows, "time_sec"):
        issues.append("time_sec is not monotonic")
    return result(exp_dir, "metric_snapshot_schema", rows, ["metric_snapshots.jsonl"], issues)


def validate_mission_event_contract(exp_dir: Path) -> dict[str, str]:
    path = exp_dir / "mission_events.jsonl"
    rows = read_jsonl(path)
    issues = []
    if not rows:
        issues.append("mission_events.jsonl is empty")
    for idx, row in enumerate(rows[:250], start=1):
        issues.extend(prefix(idx, missing_fields(row, REQUIRED_MISSION_EVENT_FIELDS)))
        message = row.get("message") or {}
        issues.extend(prefix(idx, missing_fields(message, REQUIRED_MESSAGE_FIELDS), "message."))
    if rows and not is_monotonic(rows, "time_sec"):
        issues.append("time_sec is not monotonic")
    return result(exp_dir, "mission_event_schema", rows, ["mission_events.jsonl"], issues)


def validate_trace_contract(exp_dir: Path, filename: str, agent_prefix: str) -> dict[str, str]:
    path = exp_dir / filename
    rows = read_jsonl(path)
    required_files = [filename]
    issues = []
    if not path.exists():
        return result(exp_dir, f"{agent_prefix.lower()}_decision_trace_schema", rows, required_files, [])
    if not rows:
        issues.append(f"{filename} is empty")
    for idx, row in enumerate(rows, start=1):
        issues.extend(prefix(idx, missing_fields(row, REQUIRED_TRACE_FIELDS)))
        if not str(row.get("agent", "")).startswith(agent_prefix):
            issues.append(f"row {idx}: agent does not start with {agent_prefix}")
        observation = row.get("observation") or {}
        signals = observation.get("signals") or {}
        issues.extend(prefix(idx, missing_fields(observation, REQUIRED_OBSERVATION_FIELDS), "observation."))
        issues.extend(prefix(idx, missing_fields(signals, REQUIRED_OBSERVATION_SIGNAL_FIELDS), "observation.signals."))
        if not isinstance(row.get("tool_calls"), list):
            issues.append(f"row {idx}: tool_calls must be a list")
        if not isinstance(row.get("candidate_actions"), list):
            issues.append(f"row {idx}: candidate_actions must be a list")
        if not isinstance(row.get("selected_action"), dict):
            issues.append(f"row {idx}: selected_action must be an object")
    if rows and not is_monotonic(rows, "time_sec"):
        issues.append("time_sec is not monotonic")
    return result(exp_dir, f"{agent_prefix.lower()}_decision_trace_schema", rows, required_files, issues)


def validate_cross_contract(exp_dir: Path) -> dict[str, str]:
    attack_rows = read_jsonl(exp_dir / "attack_events.jsonl")
    defense_rows = read_jsonl(exp_dir / "defense_events.jsonl")
    metric_rows = read_jsonl(exp_dir / "metric_snapshots.jsonl")
    aura_traces = read_jsonl(exp_dir / "aura_decision_traces.jsonl")
    tsra_traces = read_jsonl(exp_dir / "tsra_r_decision_traces.jsonl")
    issues = []

    attack_ids = {row.get("event_id") for row in attack_rows}
    traced_attack_ids = {
        row.get("selected_action", {}).get("event_id")
        for row in aura_traces
        if row.get("selected_action", {}).get("type") == "attack_event"
    }
    missing_attack_traces = sorted(str(event_id) for event_id in attack_ids - traced_attack_ids if event_id)
    if missing_attack_traces and any(row.get("agent") != "fixed" for row in attack_rows):
        issues.append(f"attack events without AURA trace: {', '.join(missing_attack_traces[:5])}")

    defense_event_traces = [
        row for row in tsra_traces if row.get("selected_action", {}).get("type") == "defense_events"
    ]
    if defense_rows and not defense_event_traces:
        issues.append("defense events exist but no TSRA-R trace selected defense_events")

    if attack_rows and metric_rows:
        first_attack_time = min(as_float(row.get("selected_at")) for row in attack_rows)
        last_metric_time = max(as_float(row.get("time_sec")) for row in metric_rows)
        if last_metric_time < first_attack_time:
            issues.append("metric snapshots end before first attack")

    if defense_rows and metric_rows:
        first_defense_time = min(as_float(row.get("time_sec")) for row in defense_rows)
        last_metric_time = max(as_float(row.get("time_sec")) for row in metric_rows)
        if last_metric_time < first_defense_time:
            issues.append("metric snapshots end before first defense")

    return result(
        exp_dir,
        "agent_cross_contract",
        attack_rows + defense_rows + metric_rows,
        [
            "attack_events.jsonl",
            "defense_events.jsonl",
            "metric_snapshots.jsonl",
            "aura_decision_traces.jsonl",
            "tsra_r_decision_traces.jsonl",
        ],
        issues,
    )


def prefix(row_number: int, fields: list[str], prefix_text: str = "") -> list[str]:
    return [f"row {row_number}: missing {prefix_text}{field}" for field in fields]


def result(
    exp_dir: Path,
    contract: str,
    checked_rows: list[dict[str, Any]],
    required_files: list[str],
    issues: list[str],
) -> dict[str, str]:
    decode_issues = [
        f"decode error: {row['__decode_error__']}"
        for row in checked_rows
        if "__decode_error__" in row
    ]
    all_issues = decode_issues + issues
    return {
        "experiment": exp_dir.name,
        "contract": contract,
        "status": "pass" if not all_issues else "fail",
        "checked_rows": str(len(checked_rows)),
        "required_files": ", ".join(required_files),
        "issues": " || ".join(all_issues),
    }


def discover_experiments(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir())


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Contract Validation",
        "",
        "This table validates the interface contract between AURA, TSRA-R, and MissionSimulator logs.",
        "",
        f"Safety boundary: {SIMULATION_SAFETY_TEXT}",
        "",
        "| experiment | contract | status | checked_rows | issues |",
        "|---|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_cell(row["experiment"]),
                    markdown_cell(row["contract"]),
                    markdown_cell(row["status"]),
                    markdown_cell(row["checked_rows"]),
                    markdown_cell(row["issues"] or "none"),
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate AURA/TSRA-R event and trace contracts.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any contract row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    experiments = discover_experiments(args.experiment_root)
    rows: list[dict[str, str]] = []
    for exp_dir in experiments:
        rows.extend(validate_experiment(exp_dir))
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failures = [row for row in rows if row["status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} contract checks)")
    print(f"Wrote {args.output_md} ({len(rows)} contract checks)")
    if failures:
        print(f"Failed contract checks: {len(failures)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
