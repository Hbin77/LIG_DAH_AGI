from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_tool_usage_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_tool_usage_audit.md")

TRACE_FILES = [
    "aura_decision_traces.jsonl",
    "tsra_r_decision_traces.jsonl",
    "tsra_r_rule_delegate_traces.jsonl",
]

SAFETY_BOUNDARY = (
    "closed simulation agent-tool audit only; no RF, exploit, or live network action"
)

TOOL_ROLES = {
    "generate_attack_candidates": "AURA attack candidate generation",
    "estimate_candidate_effect": "AURA analytic mission-impact what-if estimate",
    "estimate_detectability": "AURA detectability penalty estimate",
    "predict_candidate_impact": "AURA ML impact prediction",
    "evaluate_defense_conditions": "TSRA-R defense condition evaluation",
    "select_fallback_link": "TSRA-R PACE fallback selection",
    "predict_attack_probability": "TSRA-R ML anomaly probability prediction",
    "assess_mission_risk_guard": "TSRA-R ML residual mission-risk guard assessment",
    "execute_rule_defense_actions": "TSRA-R ML defense-window rule action execution",
    "summarize_attack_context": "TSRA-R cross-agent AURA attack context summary",
    "summarize_defense_context": "AURA cross-agent TSRA-R defense context summary",
}

FIELDNAMES = [
    "experiment",
    "agent",
    "policy",
    "tool_name",
    "tool_role",
    "trace_count",
    "traces_with_tool",
    "trace_coverage",
    "invocation_count",
    "ok_count",
    "error_count",
    "input_summary_coverage",
    "output_summary_coverage",
    "distinct_input_signature_count",
    "distinct_output_signature_count",
    "sample_input_keys",
    "sample_output_keys",
    "decision_link",
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
            for (agent, policy), trace_rows in sorted(by_agent_policy.items()):
                groups.append((exp_dir.name, agent, policy, trace_rows))
    return groups


def collect_rows(experiment_root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for experiment, agent, policy, traces in discover_trace_groups(experiment_root):
        rows.extend(audit_group(experiment, agent, policy, traces))
    return rows


def audit_group(
    experiment: str,
    agent: str,
    policy: str,
    traces: list[dict[str, Any]],
) -> list[dict[str, str]]:
    trace_count = len(traces)
    calls_by_tool: dict[str, list[dict[str, Any]]] = {}
    trace_ids_by_tool: dict[str, set[str]] = {}
    for index, trace in enumerate(traces):
        trace_id = str(trace.get("trace_id") or f"trace-{index}")
        for call in trace.get("tool_calls") or []:
            tool_name = str(call.get("tool_name") or "")
            if not tool_name:
                continue
            calls_by_tool.setdefault(tool_name, []).append(call)
            trace_ids_by_tool.setdefault(tool_name, set()).add(trace_id)

    rows = []
    for tool_name in sorted(calls_by_tool):
        calls = calls_by_tool[tool_name]
        traces_with_tool = len(trace_ids_by_tool.get(tool_name, set()))
        ok_count = sum(1 for call in calls if call.get("status") == "ok")
        error_count = sum(1 for call in calls if call.get("status") != "ok")
        input_coverage = coverage(
            calls,
            lambda call: isinstance(call.get("input_summary"), dict)
            and bool(call.get("input_summary")),
        )
        output_coverage = coverage(calls, lambda call: "output_summary" in call)
        input_signatures = {stable_json(call.get("input_summary")) for call in calls}
        output_signatures = {stable_json(call.get("output_summary")) for call in calls}
        issues = evaluate_issues(
            invocation_count=len(calls),
            error_count=error_count,
            input_coverage=input_coverage,
            output_coverage=output_coverage,
        )
        rows.append(
            {
                "experiment": experiment,
                "agent": agent,
                "policy": policy,
                "tool_name": tool_name,
                "tool_role": TOOL_ROLES.get(tool_name, "Agent tool invocation"),
                "trace_count": str(trace_count),
                "traces_with_tool": str(traces_with_tool),
                "trace_coverage": format_ratio(
                    traces_with_tool / trace_count if trace_count else 0.0
                ),
                "invocation_count": str(len(calls)),
                "ok_count": str(ok_count),
                "error_count": str(error_count),
                "input_summary_coverage": format_ratio(input_coverage),
                "output_summary_coverage": format_ratio(output_coverage),
                "distinct_input_signature_count": str(len(input_signatures)),
                "distinct_output_signature_count": str(len(output_signatures)),
                "sample_input_keys": sample_keys(calls, "input_summary"),
                "sample_output_keys": sample_keys(calls, "output_summary"),
                "decision_link": decision_link(agent, tool_name),
                "status": "pass" if not issues else "fail",
                "issues": " || ".join(issues),
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return rows


def coverage(rows: list[dict[str, Any]], predicate: Any) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if predicate(row)) / len(rows)


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def format_ratio(value: float) -> str:
    return f"{value:.6g}"


def evaluate_issues(
    *,
    invocation_count: int,
    error_count: int,
    input_coverage: float,
    output_coverage: float,
) -> list[str]:
    issues = []
    if invocation_count <= 0:
        issues.append("no invocations")
    if error_count > 0:
        issues.append(f"tool errors={error_count}")
    if input_coverage < 1.0:
        issues.append(f"input summary coverage below 1.0: {format_ratio(input_coverage)}")
    if output_coverage < 1.0:
        issues.append(f"output summary coverage below 1.0: {format_ratio(output_coverage)}")
    return issues


def sample_keys(calls: list[dict[str, Any]], field: str) -> str:
    for call in calls:
        value = call.get(field)
        if isinstance(value, dict):
            return ", ".join(sorted(str(key) for key in value.keys())) or "none"
        if isinstance(value, list):
            return "list"
        if value is not None:
            return type(value).__name__
    return "none"


def decision_link(agent: str, tool_name: str) -> str:
    if tool_name == "generate_attack_candidates":
        return "candidate_actions are generated before AURA ranks attack effects"
    if tool_name == "estimate_candidate_effect":
        return "mission impact estimates feed AURA score calculation"
    if tool_name == "estimate_detectability":
        return "detectability penalty is subtracted from AURA attack score"
    if tool_name == "predict_candidate_impact":
        return "ML impact prediction feeds AURA-ML candidate ranking"
    if tool_name == "evaluate_defense_conditions":
        return "condition outputs drive TSRA-R defense action candidates"
    if tool_name == "select_fallback_link":
        return "PACE fallback selection drives TSRA-R pace_switch details"
    if tool_name == "predict_attack_probability":
        return "ML anomaly probability opens TSRA-R reactive defense window"
    if tool_name == "assess_mission_risk_guard":
        return "Residual mission risk can extend a previously opened TSRA-R-ML defense window"
    if tool_name == "execute_rule_defense_actions":
        return "ML-opened defense windows delegate bounded core defense actions through a recorded runtime tool"
    if tool_name == "summarize_attack_context":
        return "AURA attack context feeds TSRA-R memory, candidates, feedback, and event details"
    if tool_name == "summarize_defense_context":
        return "TSRA-R defense context feeds AURA memory, candidates, feedback, and counter-defense selection"
    return f"{agent} decision trace records this tool before selected_action"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Tool Usage Audit",
        "",
        "This audit verifies that agent tools are actually invoked inside DecisionTrace records with input and output summaries.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'status'))}",
        f"- Tools: {', '.join(sorted({row['tool_name'] for row in rows}))}",
        "",
        "## Tool Table",
        "",
    ]
    visible_fields = [
        "experiment",
        "agent",
        "policy",
        "tool_name",
        "invocation_count",
        "trace_coverage",
        "status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))

    lines.extend(["", "## By Tool", ""])
    for tool_name in sorted({row["tool_name"] for row in rows}):
        subset = [row for row in rows if row["tool_name"] == tool_name]
        total_invocations = sum(int(row["invocation_count"]) for row in subset)
        lines.extend(
            [
                f"### {tool_name}",
                "",
                f"- Role: {subset[0]['tool_role']}",
                f"- Rows: {len(subset)}",
                f"- Total invocations: {total_invocations}",
                f"- Status: {format_counts(count_values(subset, 'status'))}",
                f"- Decision link: {subset[0]['decision_link']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def count_values(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row[field]
        counts[value] = counts.get(value, 0) + 1
    return counts


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def markdown_row(values: list[str]) -> str:
    return "| " + " | ".join(values) + " |"


def markdown_cell(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit AgentTool usage from DecisionTrace logs.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.experiment_root)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} tool audit rows)")
    print(f"Wrote {args.output_md} ({len(rows)} tool audit rows)")


if __name__ == "__main__":
    main()
