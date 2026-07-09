from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_runtime_invariant_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_runtime_invariant_audit.md")

TRACE_FILES = [
    "aura_decision_traces.jsonl",
    "tsra_r_decision_traces.jsonl",
]

MEMORY_CAP = 24
SAFETY_BOUNDARY = (
    "closed simulation agent-runtime invariant audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "trace_file",
    "agent",
    "policy",
    "trace_count",
    "trace_id_unique",
    "trace_id_sequence_ok",
    "time_monotonic",
    "observation_count_expected",
    "decision_count_expected",
    "last_selected_chain_checked",
    "last_selected_chain_matched",
    "last_selected_chain_match_rate",
    "tool_invocation_count",
    "tool_error_count",
    "candidate_action_coverage",
    "non_noop_count",
    "selected_event_count",
    "runtime_components",
    "status",
    "issues",
    "safety_boundary",
]


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


def discover_trace_groups(root: Path) -> list[tuple[str, str, str, str, list[dict[str, Any]]]]:
    groups: list[tuple[str, str, str, str, list[dict[str, Any]]]] = []
    if not root.exists():
        return groups
    for exp_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        for filename in TRACE_FILES:
            rows = read_jsonl(exp_dir / filename)
            if not rows:
                continue
            grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
            for row in rows:
                key = (str(row.get("agent", "")), str(row.get("policy", "")))
                grouped.setdefault(key, []).append(row)
            for (agent, policy), trace_rows in sorted(grouped.items()):
                groups.append((exp_dir.name, filename, agent, policy, trace_rows))
    return groups


def audit_group(
    experiment: str,
    trace_file: str,
    agent: str,
    policy: str,
    traces: list[dict[str, Any]],
) -> dict[str, str]:
    trace_ids = [str(trace.get("trace_id", "")) for trace in traces]
    times = [as_float(trace.get("time_sec")) for trace in traces]
    trace_id_unique = len(trace_ids) == len(set(trace_ids))
    trace_id_sequence_ok = has_contiguous_trace_suffixes(trace_ids)
    time_monotonic = nondecreasing(times)

    observation_count_expected = memory_count_matches(
        traces,
        field="observation_count",
        offset=1,
    )
    decision_count_expected = memory_count_matches(
        traces,
        field="decision_count",
        offset=0,
    )
    chain_checked, chain_matched = last_selected_chain_counts(traces)
    chain_rate = chain_matched / chain_checked if chain_checked else 0.0

    tool_calls = [
        call
        for trace in traces
        for call in trace.get("tool_calls", [])
        if isinstance(call, dict)
    ]
    tool_error_count = sum(1 for call in tool_calls if call.get("status") != "ok")
    candidate_action_coverage = coverage(
        traces,
        lambda trace: bool(trace.get("candidate_actions")),
    )
    non_noop_count = sum(
        1
        for trace in traces
        if (trace.get("selected_action") or {}).get("type") not in ("", None, "no_op")
    )
    selected_event_count = sum(selected_event_count_for_trace(trace) for trace in traces)
    components = observed_runtime_components(traces, tool_calls)

    issues = evaluate_issues(
        traces=traces,
        trace_id_unique=trace_id_unique,
        trace_id_sequence_ok=trace_id_sequence_ok,
        time_monotonic=time_monotonic,
        observation_count_expected=observation_count_expected,
        decision_count_expected=decision_count_expected,
        chain_checked=chain_checked,
        chain_rate=chain_rate,
        tool_invocation_count=len(tool_calls),
        tool_error_count=tool_error_count,
        non_noop_count=non_noop_count,
        selected_event_count=selected_event_count,
        components=components,
    )

    return {
        "experiment": experiment,
        "trace_file": trace_file,
        "agent": agent,
        "policy": policy,
        "trace_count": str(len(traces)),
        "trace_id_unique": str(trace_id_unique).lower(),
        "trace_id_sequence_ok": str(trace_id_sequence_ok).lower(),
        "time_monotonic": str(time_monotonic).lower(),
        "observation_count_expected": str(observation_count_expected).lower(),
        "decision_count_expected": str(decision_count_expected).lower(),
        "last_selected_chain_checked": str(chain_checked),
        "last_selected_chain_matched": str(chain_matched),
        "last_selected_chain_match_rate": format_ratio(chain_rate),
        "tool_invocation_count": str(len(tool_calls)),
        "tool_error_count": str(tool_error_count),
        "candidate_action_coverage": format_ratio(candidate_action_coverage),
        "non_noop_count": str(non_noop_count),
        "selected_event_count": str(selected_event_count),
        "runtime_components": ", ".join(components),
        "status": "pass" if not issues else "fail",
        "issues": " || ".join(issues),
        "safety_boundary": SAFETY_BOUNDARY,
    }


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def nondecreasing(values: list[float]) -> bool:
    return all(after >= before for before, after in zip(values, values[1:]))


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def format_ratio(value: float) -> str:
    return f"{value:.6g}"


def has_contiguous_trace_suffixes(trace_ids: list[str]) -> bool:
    suffixes = []
    for trace_id in trace_ids:
        match = re.search(r"-(\d+)$", trace_id)
        if not match:
            return False
        suffixes.append(int(match.group(1)))
    return suffixes == list(range(1, len(trace_ids) + 1))


def memory_count_matches(
    traces: list[dict[str, Any]],
    *,
    field: str,
    offset: int,
) -> bool:
    for index, trace in enumerate(traces):
        memory = trace.get("memory") or {}
        if not isinstance(memory, dict):
            return False
        expected = min(index + offset, MEMORY_CAP)
        if as_float(memory.get(field), default=-1.0) != expected:
            return False
    return True


def last_selected_chain_counts(traces: list[dict[str, Any]]) -> tuple[int, int]:
    checked = 0
    matched = 0
    for previous, current in zip(traces, traces[1:]):
        last_selected = (current.get("memory") or {}).get("last_selected_action")
        if not last_selected:
            continue
        checked += 1
        if stable_json(previous.get("selected_action") or {}) == stable_json(last_selected):
            matched += 1
    return checked, matched


def coverage(rows: list[dict[str, Any]], predicate: Any) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if predicate(row)) / len(rows)


def selected_event_count_for_trace(trace: dict[str, Any]) -> int:
    selected = trace.get("selected_action") or {}
    selected_type = selected.get("type")
    if selected_type == "attack_event" and selected.get("event_id"):
        return 1
    if selected_type == "defense_events":
        return len(selected.get("events") or [])
    return 0


def observed_runtime_components(
    traces: list[dict[str, Any]],
    tool_calls: list[dict[str, Any]],
) -> list[str]:
    components = []
    if all(isinstance(trace.get("observation"), dict) for trace in traces):
        components.append("observation")
    if all(isinstance(trace.get("memory"), dict) for trace in traces):
        components.append("memory")
    if tool_calls:
        components.append("tool")
    if any(trace.get("candidate_actions") for trace in traces):
        components.append("candidate_actions")
    if all(isinstance(trace.get("selected_action"), dict) for trace in traces):
        components.append("selected_action")
    if all(isinstance(trace.get("feedback"), dict) for trace in traces):
        components.append("feedback")
    if all(trace.get("reason") for trace in traces):
        components.append("reason")
    return components


def evaluate_issues(
    *,
    traces: list[dict[str, Any]],
    trace_id_unique: bool,
    trace_id_sequence_ok: bool,
    time_monotonic: bool,
    observation_count_expected: bool,
    decision_count_expected: bool,
    chain_checked: int,
    chain_rate: float,
    tool_invocation_count: int,
    tool_error_count: int,
    non_noop_count: int,
    selected_event_count: int,
    components: list[str],
) -> list[str]:
    issues = []
    if not traces:
        issues.append("no traces")
    if not trace_id_unique:
        issues.append("trace ids are not unique")
    if not trace_id_sequence_ok:
        issues.append("trace id suffixes are not contiguous")
    if not time_monotonic:
        issues.append("trace time is not monotonic")
    if not observation_count_expected:
        issues.append("memory observation_count does not match runtime sequence")
    if not decision_count_expected:
        issues.append("memory decision_count does not match runtime sequence")
    if chain_checked < max(0, len(traces) - 1):
        issues.append("last_selected_action chain is incomplete")
    if chain_checked and chain_rate < 1.0:
        issues.append(f"last_selected_action chain match below 1.0: {format_ratio(chain_rate)}")
    if tool_invocation_count <= 0:
        issues.append("no agent tool invocations")
    if tool_error_count > 0:
        issues.append(f"tool error count={tool_error_count}")
    if non_noop_count <= 0:
        issues.append("no non-no-op decisions")
    if selected_event_count <= 0:
        issues.append("no selected attack/defense event")
    required_components = {
        "observation",
        "memory",
        "tool",
        "candidate_actions",
        "selected_action",
        "feedback",
        "reason",
    }
    missing_components = sorted(required_components - set(components))
    if missing_components:
        issues.append(f"missing runtime components: {', '.join(missing_components)}")
    return issues


def collect_rows(experiment_root: Path) -> list[dict[str, str]]:
    return [
        audit_group(experiment, trace_file, agent, policy, traces)
        for experiment, trace_file, agent, policy, traces in discover_trace_groups(experiment_root)
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    visible_fields = [
        "experiment",
        "agent",
        "policy",
        "trace_count",
        "trace_id_sequence_ok",
        "decision_count_expected",
        "tool_error_count",
        "status",
        "issues",
    ]
    lines = [
        "# Agent Runtime Invariant Audit",
        "",
        "This audit checks runtime-level invariants across DecisionTrace logs.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(rows)}",
        "",
        "## Runtime Invariants",
        "",
        markdown_row(visible_fields),
        markdown_row(["---"] * len(visible_fields)),
    ]
    for row in rows:
        lines.append(markdown_row([markdown_cell(row.get(field, "")) for field in visible_fields]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_counts(rows: list[dict[str, str]]) -> str:
    counts = {
        status: sum(1 for row in rows if row.get("status") == status)
        for status in sorted({row.get("status", "") for row in rows})
    }
    return ", ".join(f"{key}={value}" for key, value in counts.items())


def markdown_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value) for value in values) + " |"


def markdown_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit AgentRuntime invariants from DecisionTrace logs.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any runtime invariant row fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.experiment_root)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failures = [row for row in rows if row["status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} rows)")
    print(f"Wrote {args.output_md} ({len(rows)} rows)")
    if failures:
        print(f"Failed runtime invariant rows: {len(failures)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
