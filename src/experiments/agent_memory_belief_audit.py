from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_memory_belief_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_memory_belief_audit.md")

TRACE_FILES = [
    "aura_decision_traces.jsonl",
    "tsra_r_decision_traces.jsonl",
]

SAFETY_BOUNDARY = (
    "closed simulation agent-memory audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "agent",
    "policy",
    "trace_count",
    "memory_coverage",
    "observation_count_start",
    "observation_count_end",
    "observation_count_nondecreasing",
    "decision_count_start",
    "decision_count_end",
    "decision_count_nondecreasing",
    "memory_signature_count",
    "belief_keys",
    "changing_belief_keys",
    "feedback_keys",
    "last_selected_chain_checked",
    "last_selected_chain_matched",
    "last_selected_chain_match_rate",
    "memory_effect_summary",
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
            grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
            for row in rows:
                key = (str(row.get("agent", "")), str(row.get("policy", "")))
                grouped.setdefault(key, []).append(row)
            for (agent, policy), trace_rows in sorted(grouped.items()):
                groups.append(
                    (
                        exp_dir.name,
                        agent,
                        policy,
                        sorted(trace_rows, key=lambda row: as_float(row.get("time_sec"))),
                    )
                )
    return groups


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def format_ratio(value: float) -> str:
    return f"{value:.6g}"


def format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, list):
        return "[" + ",".join(str(item) for item in value) + "]"
    if value is None:
        return ""
    return str(value)


def nondecreasing(values: list[float]) -> bool:
    return all(after >= before for before, after in zip(values, values[1:]))


def audit_group(
    experiment: str,
    agent: str,
    policy: str,
    traces: list[dict[str, Any]],
) -> dict[str, str]:
    memories = [trace.get("memory") for trace in traces]
    valid_memories = [memory for memory in memories if isinstance(memory, dict)]
    memory_coverage = len(valid_memories) / len(traces) if traces else 0.0

    observation_counts = [
        as_float(memory.get("observation_count"))
        for memory in valid_memories
        if "observation_count" in memory
    ]
    decision_counts = [
        as_float(memory.get("decision_count"))
        for memory in valid_memories
        if "decision_count" in memory
    ]
    belief_states = [
        memory.get("belief_state") or {}
        for memory in valid_memories
        if isinstance(memory.get("belief_state") or {}, dict)
    ]
    belief_keys = sorted({key for belief in belief_states for key in belief})
    changing_belief_keys = changing_keys(belief_states, belief_keys)
    feedback_keys = sorted(
        {
            key
            for trace in traces
            for key in (trace.get("feedback") or {})
            if isinstance(trace.get("feedback"), dict)
        }
    )
    memory_signature_count = len({stable_json(memory) for memory in valid_memories})
    chain_checked, chain_matched = last_selected_chain_counts(traces)
    chain_rate = chain_matched / chain_checked if chain_checked else 0.0

    issues = evaluate_issues(
        agent=agent,
        traces=traces,
        memory_coverage=memory_coverage,
        observation_counts=observation_counts,
        decision_counts=decision_counts,
        memory_signature_count=memory_signature_count,
        belief_keys=belief_keys,
        changing_belief_keys=changing_belief_keys,
        feedback_keys=feedback_keys,
        chain_checked=chain_checked,
        chain_rate=chain_rate,
    )

    return {
        "experiment": experiment,
        "agent": agent,
        "policy": policy,
        "trace_count": str(len(traces)),
        "memory_coverage": format_ratio(memory_coverage),
        "observation_count_start": count_endpoint(observation_counts, first=True),
        "observation_count_end": count_endpoint(observation_counts, first=False),
        "observation_count_nondecreasing": str(nondecreasing(observation_counts)).lower(),
        "decision_count_start": count_endpoint(decision_counts, first=True),
        "decision_count_end": count_endpoint(decision_counts, first=False),
        "decision_count_nondecreasing": str(nondecreasing(decision_counts)).lower(),
        "memory_signature_count": str(memory_signature_count),
        "belief_keys": ", ".join(belief_keys) if belief_keys else "none",
        "changing_belief_keys": ", ".join(changing_belief_keys)
        if changing_belief_keys
        else "none",
        "feedback_keys": ", ".join(feedback_keys) if feedback_keys else "none",
        "last_selected_chain_checked": str(chain_checked),
        "last_selected_chain_matched": str(chain_matched),
        "last_selected_chain_match_rate": format_ratio(chain_rate),
        "memory_effect_summary": memory_effect_summary(agent, changing_belief_keys, feedback_keys),
        "status": "pass" if not issues else "fail",
        "issues": " || ".join(issues),
        "safety_boundary": SAFETY_BOUNDARY,
    }


def changing_keys(
    belief_states: list[dict[str, Any]],
    keys: list[str],
) -> list[str]:
    changed = []
    for key in keys:
        values = {stable_json(belief.get(key)) for belief in belief_states}
        if len(values) > 1:
            changed.append(key)
    return changed


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


def evaluate_issues(
    *,
    agent: str,
    traces: list[dict[str, Any]],
    memory_coverage: float,
    observation_counts: list[float],
    decision_counts: list[float],
    memory_signature_count: int,
    belief_keys: list[str],
    changing_belief_keys: list[str],
    feedback_keys: list[str],
    chain_checked: int,
    chain_rate: float,
) -> list[str]:
    issues = []
    if not traces:
        issues.append("no traces")
    if memory_coverage < 1.0:
        issues.append(f"memory coverage below 1.0: {format_ratio(memory_coverage)}")
    if not observation_counts or not nondecreasing(observation_counts):
        issues.append("observation_count is missing or not nondecreasing")
    if not decision_counts or not nondecreasing(decision_counts):
        issues.append("decision_count is missing or not nondecreasing")
    if memory_signature_count < 2:
        issues.append("memory signatures do not change")
    if not feedback_keys:
        issues.append("feedback keys are missing")
    if chain_checked < max(0, len(traces) - 1):
        issues.append("last_selected_action chain is incomplete")
    if chain_checked and chain_rate < 1.0:
        issues.append(f"last_selected_action chain match below 1.0: {format_ratio(chain_rate)}")

    required_belief_keys = required_keys_for_agent(agent)
    missing_keys = sorted(required_belief_keys - set(belief_keys))
    if missing_keys:
        issues.append(f"missing belief keys: {', '.join(missing_keys)}")
    if required_belief_keys and not (required_belief_keys & set(changing_belief_keys)):
        issues.append("required belief keys never changed")
    return issues


def required_keys_for_agent(agent: str) -> set[str]:
    if agent.startswith("AURA"):
        return {"event_count", "last_attack_time", "last_attack_type"}
    if agent == "TSRA-R-ML":
        return {"active_defense_until", "last_probability"}
    if agent.startswith("TSRA-R"):
        return {"action_cooldowns", "event_count", "mode"}
    return set()


def count_endpoint(values: list[float], *, first: bool) -> str:
    if not values:
        return ""
    value = values[0] if first else values[-1]
    if value.is_integer():
        return str(int(value))
    return format_ratio(value)


def memory_effect_summary(
    agent: str,
    changing_belief_keys: list[str],
    feedback_keys: list[str],
) -> str:
    changed = ", ".join(changing_belief_keys) if changing_belief_keys else "none"
    feedback = ", ".join(feedback_keys) if feedback_keys else "none"
    if agent.startswith("AURA"):
        return (
            "AURA memory carries attack cadence and last attack context into later "
            f"candidate decisions; changing={changed}; feedback={feedback}."
        )
    if agent == "TSRA-R-ML":
        return (
            "ML TSRA-R memory carries anomaly probability and active defense window "
            f"state into reactive defense decisions; changing={changed}; feedback={feedback}."
        )
    if agent.startswith("TSRA-R"):
        return (
            "TSRA-R memory carries cooldown, enabled action, and event count state into "
            f"bounded response decisions; changing={changed}; feedback={feedback}."
        )
    return f"Memory state changed across the closed-loop trace; changing={changed}; feedback={feedback}."


def collect_rows(experiment_root: Path) -> list[dict[str, str]]:
    return [
        audit_group(experiment, agent, policy, traces)
        for experiment, agent, policy, traces in discover_trace_groups(experiment_root)
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Memory Belief Audit",
        "",
        "This audit verifies that AgentMemory is populated, evolves across decisions, and carries the previous selected action into the next decision loop.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Audit rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'status'))}",
        f"- Agents: {', '.join(sorted({row['agent'] for row in rows}))}",
        "",
        "## Audit Table",
        "",
    ]
    visible_fields = [
        "experiment",
        "agent",
        "policy",
        "trace_count",
        "memory_signature_count",
        "changing_belief_keys",
        "last_selected_chain_match_rate",
        "status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['experiment']} {row['agent']} {row['policy']}",
                "",
                f"- Memory coverage: {row['memory_coverage']}",
                f"- Observation count: {row['observation_count_start']} -> {row['observation_count_end']} ({row['observation_count_nondecreasing']})",
                f"- Decision count: {row['decision_count_start']} -> {row['decision_count_end']} ({row['decision_count_nondecreasing']})",
                f"- Belief keys: {row['belief_keys']}",
                f"- Changing belief keys: {row['changing_belief_keys']}",
                f"- Feedback keys: {row['feedback_keys']}",
                f"- Last-selected chain: {row['last_selected_chain_matched']}/{row['last_selected_chain_checked']}",
                f"- Effect summary: {row['memory_effect_summary']}",
                f"- Status: {row['status']}",
                f"- Issues: {row['issues'] or 'none'}",
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
    parser = argparse.ArgumentParser(description="Audit AgentMemory and belief-state behavior.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.experiment_root)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} memory audit rows)")
    print(f"Wrote {args.output_md} ({len(rows)} memory audit rows)")


if __name__ == "__main__":
    main()
