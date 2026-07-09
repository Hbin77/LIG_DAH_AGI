from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_decision_causality_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_decision_causality_audit.md")

TRACE_FILES = [
    "aura_decision_traces.jsonl",
    "tsra_r_decision_traces.jsonl",
]

SAFETY_BOUNDARY = (
    "closed simulation decision-causality audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "trace_id",
    "time_sec",
    "agent",
    "policy",
    "selected_type",
    "selected_actions",
    "candidate_count",
    "top_candidate_actions",
    "matched_candidate_actions",
    "required_tools",
    "observed_tools",
    "candidate_support",
    "tool_support",
    "score_or_threshold_support",
    "causal_status",
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


def discover_traces(root: Path) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    if not root.exists():
        return rows
    for exp_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        for filename in TRACE_FILES:
            for trace in read_jsonl(exp_dir / filename):
                rows.append((exp_dir.name, trace))
    return rows


def collect_rows(experiment_root: Path) -> list[dict[str, str]]:
    rows = [
        audit_trace(experiment, trace)
        for experiment, trace in discover_traces(experiment_root)
    ]
    return sorted(
        rows,
        key=lambda row: (
            row["experiment"],
            float(row["time_sec"] or 0.0),
            row["agent"],
            row["trace_id"],
        ),
    )


def audit_trace(experiment: str, trace: dict[str, Any]) -> dict[str, str]:
    selected = trace.get("selected_action") or {}
    candidates = trace.get("candidate_actions") or []
    selected_type = str(selected.get("type") or "")
    selected_actions = selected_action_names(selected)
    observed_tools = tool_names(trace)
    required_tools = required_tools_for_trace(trace)

    candidate_support, matched_actions = evaluate_candidate_support(
        trace=trace,
        selected=selected,
        candidates=candidates,
    )
    tool_support = "pass" if set(required_tools).issubset(set(observed_tools)) else "fail"
    score_support = evaluate_score_or_threshold_support(selected, candidates, trace)
    issues = []
    if candidate_support == "fail":
        issues.append("selected action is not supported by candidate_actions")
    if tool_support == "fail":
        missing_tools = sorted(set(required_tools) - set(observed_tools))
        issues.append(f"missing required tools: {', '.join(missing_tools)}")
    if score_support == "fail":
        issues.append("selected action is not top-scored or threshold-supported")

    return {
        "experiment": experiment,
        "trace_id": str(trace.get("trace_id") or ""),
        "time_sec": format_value(trace.get("time_sec")),
        "agent": str(trace.get("agent") or ""),
        "policy": str(trace.get("policy") or ""),
        "selected_type": selected_type,
        "selected_actions": ", ".join(selected_actions) if selected_actions else "none",
        "candidate_count": str(len(candidates)),
        "top_candidate_actions": ", ".join(top_candidate_actions(candidates)) or "none",
        "matched_candidate_actions": ", ".join(matched_actions) if matched_actions else "none",
        "required_tools": ", ".join(required_tools) if required_tools else "none",
        "observed_tools": ", ".join(observed_tools) if observed_tools else "none",
        "candidate_support": candidate_support,
        "tool_support": tool_support,
        "score_or_threshold_support": score_support,
        "causal_status": "pass" if not issues else "fail",
        "issues": " || ".join(issues),
        "safety_boundary": SAFETY_BOUNDARY,
    }


def selected_action_names(selected: dict[str, Any]) -> list[str]:
    selected_type = selected.get("type")
    if selected_type == "attack_event":
        return [str(selected.get("attack_type") or "attack_event")]
    if selected_type == "defense_events":
        return [
            str(event.get("action"))
            for event in selected.get("events") or []
            if event.get("action")
        ]
    if selected_type == "no_op":
        return ["no_op"]
    return [str(selected_type or "unknown")]


def tool_names(trace: dict[str, Any]) -> list[str]:
    names = []
    for call in trace.get("tool_calls") or []:
        name = str(call.get("tool_name") or "")
        if name and name not in names:
            names.append(name)
    return names


def required_tools_for_trace(trace: dict[str, Any]) -> list[str]:
    agent = str(trace.get("agent") or "")
    policy = str(trace.get("policy") or "")
    selected = trace.get("selected_action") or {}
    selected_type = selected.get("type")
    if agent.startswith("AURA") and selected_type == "attack_event":
        tools = ["generate_attack_candidates", "estimate_detectability"]
        if policy == "ml_impact_predictor":
            tools.append("predict_candidate_impact")
        else:
            tools.append("estimate_candidate_effect")
        return tools
    if agent == "TSRA-R-ML":
        return ["predict_attack_probability"]
    if agent.startswith("TSRA-R"):
        tools = ["evaluate_defense_conditions"]
        actions = set(selected_action_names(selected))
        if "pace_switch" in actions:
            tools.append("select_fallback_link")
        return tools
    return []


def evaluate_candidate_support(
    *,
    trace: dict[str, Any],
    selected: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> tuple[str, list[str]]:
    selected_type = selected.get("type")
    agent = str(trace.get("agent") or "")
    if selected_type == "no_op":
        return no_op_candidate_support(agent, candidates), ["no_op"]
    if selected_type == "attack_event":
        attack_type = str(selected.get("attack_type") or "")
        target_link = str(selected.get("target_link") or "")
        matches = [
            candidate
            for candidate in candidates
            if candidate.get("action") == attack_type
            and str(candidate.get("target_link") or "") == target_link
        ]
        return ("pass" if matches else "fail"), [attack_type] if matches else []
    if selected_type == "defense_events":
        selected_actions = selected_action_names(selected)
        if agent == "TSRA-R-ML":
            window_candidates = [
                candidate
                for candidate in candidates
                if candidate.get("action") == "open_defense_window"
                and threshold_supported(candidate)
            ]
            if window_candidates:
                return "pass", ["open_defense_window"]
            return "fail", []
        matched = []
        for action in selected_actions:
            matches = [
                candidate
                for candidate in candidates
                if candidate.get("action") == action
                and candidate.get("eligible") is True
                and candidate.get("ready") is True
            ]
            if matches:
                matched.append(action)
        return ("pass" if set(selected_actions).issubset(set(matched)) else "fail"), matched
    return "fail", []


def no_op_candidate_support(agent: str, candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return "pass"
    if agent == "TSRA-R-ML":
        return "pass"
    if agent.startswith("TSRA-R"):
        return "pass" if all(
            not (candidate.get("eligible") is True and candidate.get("ready") is True)
            for candidate in candidates
        ) else "fail"
    if agent.startswith("AURA"):
        return "pass"
    return "pass"


def evaluate_score_or_threshold_support(
    selected: dict[str, Any],
    candidates: list[dict[str, Any]],
    trace: dict[str, Any],
) -> str:
    selected_type = selected.get("type")
    agent = str(trace.get("agent") or "")
    if selected_type == "no_op":
        return no_op_candidate_support(agent, candidates)
    if selected_type == "attack_event":
        selected_score = as_float(selected.get("score"))
        scored = [candidate for candidate in candidates if "score" in candidate]
        if not scored:
            return "fail"
        max_score = max(as_float(candidate.get("score")) for candidate in scored)
        return "pass" if selected_score >= max_score - 1e-6 else "fail"
    if selected_type == "defense_events":
        if agent == "TSRA-R-ML":
            for candidate in candidates:
                if candidate.get("action") == "open_defense_window":
                    return "pass" if threshold_supported(candidate) else "fail"
            return "fail"
        selected_actions = selected_action_names(selected)
        for action in selected_actions:
            matches = [
                candidate
                for candidate in candidates
                if candidate.get("action") == action
                and candidate.get("eligible") is True
                and candidate.get("ready") is True
            ]
            if not matches:
                return "fail"
        return "pass"
    return "fail"


def threshold_supported(candidate: dict[str, Any]) -> bool:
    probability = as_float(candidate.get("probability"))
    threshold = as_float(candidate.get("threshold"))
    return probability >= threshold


def top_candidate_actions(candidates: list[dict[str, Any]]) -> list[str]:
    if not candidates:
        return []
    scored = [candidate for candidate in candidates if "score" in candidate]
    if scored:
        max_score = max(as_float(candidate.get("score")) for candidate in scored)
        return [
            str(candidate.get("action"))
            for candidate in scored
            if as_float(candidate.get("score")) >= max_score - 1e-6
        ]
    probabilistic = [candidate for candidate in candidates if "probability" in candidate]
    if probabilistic:
        max_probability = max(as_float(candidate.get("probability")) for candidate in probabilistic)
        return [
            str(candidate.get("action"))
            for candidate in probabilistic
            if as_float(candidate.get("probability")) >= max_probability - 1e-6
        ]
    eligible_ready = [
        candidate
        for candidate in candidates
        if candidate.get("eligible") is True and candidate.get("ready") is True
    ]
    if eligible_ready:
        return [str(candidate.get("action")) for candidate in eligible_ready]
    eligible = [candidate for candidate in candidates if candidate.get("eligible") is True]
    if eligible:
        return [str(candidate.get("action")) for candidate in eligible]
    return [str(candidates[0].get("action") or "none")]


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def format_value(value: Any) -> str:
    if value in ("", None):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Decision Causality Audit",
        "",
        "This audit verifies that selected actions are supported by candidate actions, tool calls, and score or threshold evidence inside DecisionTrace records.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'causal_status'))}",
        f"- Agents: {', '.join(sorted({row['agent'] for row in rows}))}",
        "",
        "## Support Counts",
        "",
        f"- Candidate support: {format_counts(count_values(rows, 'candidate_support'))}",
        f"- Tool support: {format_counts(count_values(rows, 'tool_support'))}",
        f"- Score or threshold support: {format_counts(count_values(rows, 'score_or_threshold_support'))}",
        "",
        "## Sample Failures",
        "",
    ]
    failures = [row for row in rows if row["causal_status"] != "pass"]
    if not failures:
        lines.append("None.")
    else:
        for row in failures[:20]:
            lines.append(
                f"- {row['experiment']} {row['trace_id']} {row['agent']} "
                f"{row['selected_actions']}: {row['issues']}"
            )
    lines.extend(
        [
            "",
            "## Audit Table",
            "",
        ]
    )
    visible_fields = [
        "experiment",
        "time_sec",
        "agent",
        "selected_actions",
        "candidate_support",
        "tool_support",
        "score_or_threshold_support",
        "causal_status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
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
    parser = argparse.ArgumentParser(description="Audit DecisionTrace action causality.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.experiment_root)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} causality audit rows)")
    print(f"Wrote {args.output_md} ({len(rows)} causality audit rows)")


if __name__ == "__main__":
    main()
