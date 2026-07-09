from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/decision_trace_quality_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/decision_trace_quality_audit.md")

TRACE_FILES = [
    "aura_decision_traces.jsonl",
    "tsra_r_decision_traces.jsonl",
]

FIELDNAMES = [
    "experiment",
    "agent",
    "policy",
    "trace_count",
    "reason_coverage",
    "observation_coverage",
    "memory_coverage",
    "feedback_coverage",
    "selected_action_coverage",
    "tool_call_coverage",
    "candidate_action_coverage",
    "non_noop_count",
    "selected_event_count",
    "distinct_tools",
    "status",
    "issues",
]

SIMULATION_SAFETY_TEXT = (
    "closed simulation trace-quality audit only; no RF, exploit, or live network action"
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def discover_trace_groups(root: Path) -> list[tuple[str, str, str, list[dict[str, Any]]]]:
    groups: list[tuple[str, str, str, list[dict[str, Any]]]] = []
    if not root.exists():
        return groups
    for exp_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        for filename in TRACE_FILES:
            rows = read_jsonl(exp_dir / filename)
            if not rows:
                continue
            by_agent_policy: dict[tuple[str, str], list[dict[str, Any]]] = {}
            for row in rows:
                key = (str(row.get("agent", "")), str(row.get("policy", "")))
                by_agent_policy.setdefault(key, []).append(row)
            for (agent, policy), grouped_rows in sorted(by_agent_policy.items()):
                groups.append((exp_dir.name, agent, policy, grouped_rows))
    return groups


def coverage(rows: list[dict[str, Any]], predicate: Any) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if predicate(row)) / len(rows)


def audit_group(
    experiment: str,
    agent: str,
    policy: str,
    traces: list[dict[str, Any]],
) -> dict[str, str]:
    trace_count = len(traces)
    reason_cov = coverage(traces, lambda row: bool(str(row.get("reason", "")).strip()))
    observation_cov = coverage(
        traces,
        lambda row: isinstance(row.get("observation"), dict)
        and bool(row.get("observation", {}).get("signals")),
    )
    memory_cov = coverage(traces, lambda row: isinstance(row.get("memory"), dict))
    feedback_cov = coverage(traces, lambda row: isinstance(row.get("feedback"), dict))
    selected_action_cov = coverage(
        traces,
        lambda row: isinstance(row.get("selected_action"), dict)
        and bool(row.get("selected_action", {}).get("type")),
    )
    tool_call_cov = coverage(traces, lambda row: bool(row.get("tool_calls")))
    candidate_action_cov = coverage(traces, lambda row: bool(row.get("candidate_actions")))
    non_noop_count = sum(
        1
        for row in traces
        if (row.get("selected_action") or {}).get("type") not in ("", None, "no_op")
    )
    selected_event_count = sum(
        selected_event_count_for_trace(row)
        for row in traces
    )
    distinct_tools = sorted(
        {
            str(tool.get("tool_name"))
            for row in traces
            for tool in row.get("tool_calls", [])
            if tool.get("tool_name")
        }
    )
    issues = evaluate_quality(
        agent=agent,
        trace_count=trace_count,
        reason_cov=reason_cov,
        observation_cov=observation_cov,
        memory_cov=memory_cov,
        feedback_cov=feedback_cov,
        selected_action_cov=selected_action_cov,
        tool_call_cov=tool_call_cov,
        candidate_action_cov=candidate_action_cov,
        non_noop_count=non_noop_count,
        selected_event_count=selected_event_count,
    )
    return {
        "experiment": experiment,
        "agent": agent,
        "policy": policy,
        "trace_count": str(trace_count),
        "reason_coverage": format_ratio(reason_cov),
        "observation_coverage": format_ratio(observation_cov),
        "memory_coverage": format_ratio(memory_cov),
        "feedback_coverage": format_ratio(feedback_cov),
        "selected_action_coverage": format_ratio(selected_action_cov),
        "tool_call_coverage": format_ratio(tool_call_cov),
        "candidate_action_coverage": format_ratio(candidate_action_cov),
        "non_noop_count": str(non_noop_count),
        "selected_event_count": str(selected_event_count),
        "distinct_tools": ", ".join(distinct_tools),
        "status": "pass" if not issues else "fail",
        "issues": " || ".join(issues),
    }


def selected_event_count_for_trace(trace: dict[str, Any]) -> int:
    selected = trace.get("selected_action") or {}
    selected_type = selected.get("type")
    if selected_type == "attack_event" and selected.get("event_id"):
        return 1
    if selected_type == "defense_events":
        return len(selected.get("events") or [])
    return 0


def evaluate_quality(
    *,
    agent: str,
    trace_count: int,
    reason_cov: float,
    observation_cov: float,
    memory_cov: float,
    feedback_cov: float,
    selected_action_cov: float,
    tool_call_cov: float,
    candidate_action_cov: float,
    non_noop_count: int,
    selected_event_count: int,
) -> list[str]:
    issues = []
    if trace_count <= 0:
        issues.append("no traces")
    required_coverages = {
        "reason": reason_cov,
        "observation": observation_cov,
        "memory": memory_cov,
        "feedback": feedback_cov,
        "selected_action": selected_action_cov,
    }
    for name, value in required_coverages.items():
        if value < 1.0:
            issues.append(f"{name} coverage below 1.0: {format_ratio(value)}")
    if non_noop_count <= 0:
        issues.append("no non-no-op selected action")
    if selected_event_count <= 0:
        issues.append("no selected attack/defense event")

    if agent.startswith("AURA"):
        if tool_call_cov <= 0:
            issues.append("AURA never called tools")
        if candidate_action_cov <= 0:
            issues.append("AURA never evaluated candidates")
    elif agent.startswith("TSRA-R"):
        if tool_call_cov < 0.95:
            issues.append(f"TSRA-R tool call coverage below 0.95: {format_ratio(tool_call_cov)}")
        if candidate_action_cov < 0.95:
            issues.append(
                f"TSRA-R candidate action coverage below 0.95: {format_ratio(candidate_action_cov)}"
            )
    return issues


def format_ratio(value: float) -> str:
    return f"{value:.6g}"


def collect_rows(experiment_root: Path) -> list[dict[str, str]]:
    groups = discover_trace_groups(experiment_root)
    return [audit_group(experiment, agent, policy, traces) for experiment, agent, policy, traces in groups]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    visible_fields = [
        "experiment",
        "agent",
        "policy",
        "trace_count",
        "tool_call_coverage",
        "candidate_action_coverage",
        "non_noop_count",
        "selected_event_count",
        "status",
        "issues",
    ]
    lines = [
        "# DecisionTrace Quality Audit",
        "",
        "This table audits whether AURA and TSRA-R traces show a complete agent decision loop.",
        "",
        f"Safety boundary: {SIMULATION_SAFETY_TEXT}",
        "",
        markdown_row(visible_fields),
        markdown_row(["---"] * len(visible_fields)),
    ]
    for row in rows:
        lines.append(markdown_row([markdown_cell(row.get(field, "")) for field in visible_fields]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value) for value in values) + " |"


def markdown_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit DecisionTrace quality for AURA and TSRA-R.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any trace quality row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.experiment_root)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failures = [row for row in rows if row["status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} audit rows)")
    print(f"Wrote {args.output_md} ({len(rows)} audit rows)")
    if failures:
        print(f"Failed trace quality rows: {len(failures)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
