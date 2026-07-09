from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENTS = [
    "E3_rule_aura",
    "E5_rule_aura_tsra_r",
    "E7_ml_aura_ml_tsra_r",
]
TRACE_FILES = [
    "aura_decision_traces.jsonl",
    "tsra_r_decision_traces.jsonl",
    "tsra_r_rule_delegate_traces.jsonl",
]
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_interface_manifest.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_interface_manifest.md")

FIELDNAMES = [
    "agent",
    "side",
    "goal",
    "policies",
    "input_contract",
    "memory_contract",
    "tool_contract",
    "candidate_contract",
    "selected_action_contract",
    "event_outputs",
    "evidence_experiments",
    "trace_count",
    "non_noop_count",
    "safety_boundary",
]

SIMULATION_SAFETY_TEXT = (
    "closed simulation agent-interface manifest only; no RF, exploit, or live network action"
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


def collect_traces(experiment_root: Path, experiments: list[str]) -> list[dict[str, Any]]:
    traces = []
    for experiment in experiments:
        exp_dir = experiment_root / experiment
        for filename in TRACE_FILES:
            for trace in read_jsonl(exp_dir / filename):
                trace["_experiment"] = experiment
                traces.append(trace)
    return traces


def build_manifest_rows(traces: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_agent: dict[str, list[dict[str, Any]]] = {}
    for trace in traces:
        by_agent.setdefault(str(trace.get("agent", "")), []).append(trace)

    rows = []
    for agent in sorted(by_agent):
        if not agent:
            continue
        rows.append(summarize_agent(agent, by_agent[agent]))
    return rows


def summarize_agent(agent: str, traces: list[dict[str, Any]]) -> dict[str, str]:
    goals = sorted({str(trace.get("goal", "")) for trace in traces if trace.get("goal")})
    policies = sorted({str(trace.get("policy", "")) for trace in traces if trace.get("policy")})
    experiments = sorted({str(trace.get("_experiment", "")) for trace in traces if trace.get("_experiment")})
    tools = sorted(
        {
            str(tool.get("tool_name", ""))
            for trace in traces
            for tool in trace.get("tool_calls", [])
            if tool.get("tool_name")
        }
    )
    candidate_actions = sorted(
        {
            str(candidate.get("action", ""))
            for trace in traces
            for candidate in trace.get("candidate_actions", [])
            if candidate.get("action")
        }
    )
    selected_types = sorted(
        {
            str((trace.get("selected_action") or {}).get("type", ""))
            for trace in traces
            if (trace.get("selected_action") or {}).get("type")
        }
    )
    emitted_actions = sorted(
        action
        for action in collect_emitted_actions(traces)
        if action
    )
    non_noop_count = sum(
        1
        for trace in traces
        if (trace.get("selected_action") or {}).get("type") not in ("", None, "no_op")
    )
    return {
        "agent": agent,
        "side": side_for_agent(agent),
        "goal": " | ".join(goals),
        "policies": ", ".join(policies),
        "input_contract": observation_contract(traces),
        "memory_contract": memory_contract(traces),
        "tool_contract": ", ".join(tools) if tools else "none",
        "candidate_contract": ", ".join(candidate_actions) if candidate_actions else "none",
        "selected_action_contract": ", ".join(selected_types) if selected_types else "none",
        "event_outputs": event_outputs_for_agent(agent, emitted_actions),
        "evidence_experiments": ", ".join(experiments),
        "trace_count": str(len(traces)),
        "non_noop_count": str(non_noop_count),
        "safety_boundary": SIMULATION_SAFETY_TEXT,
    }


def side_for_agent(agent: str) -> str:
    if agent.startswith("AURA"):
        return "attack"
    if agent.startswith("TSRA-R"):
        return "defense"
    return "unknown"


def observation_contract(traces: list[dict[str, Any]]) -> str:
    signal_keys = sorted(
        {
            str(key)
            for trace in traces
            for key in ((trace.get("observation") or {}).get("signals") or {})
        }
    )
    core = ["time_sec", "mission_phase", "active_link"]
    return ", ".join(core + [f"signals.{key}" for key in signal_keys])


def memory_contract(traces: list[dict[str, Any]]) -> str:
    memory_keys = sorted(
        {
            str(key)
            for trace in traces
            for key in (trace.get("memory") or {})
        }
    )
    belief_keys = sorted(
        {
            str(key)
            for trace in traces
            for key in ((trace.get("memory") or {}).get("belief_state") or {})
        }
    )
    parts = memory_keys + [f"belief_state.{key}" for key in belief_keys]
    return ", ".join(parts) if parts else "none"


def collect_emitted_actions(traces: list[dict[str, Any]]) -> set[str]:
    actions = set()
    for trace in traces:
        selected = trace.get("selected_action") or {}
        selected_type = selected.get("type")
        if selected_type == "attack_event":
            actions.add(str(selected.get("attack_type", "attack_event")))
        elif selected_type == "defense_events":
            for event in selected.get("events") or []:
                if event.get("action"):
                    actions.add(str(event.get("action")))
    return actions


def event_outputs_for_agent(agent: str, emitted_actions: list[str]) -> str:
    if agent.startswith("AURA"):
        return f"attack_events.jsonl: {', '.join(emitted_actions)}"
    if agent.startswith("TSRA-R"):
        return f"defense_events.jsonl: {', '.join(emitted_actions)}"
    return ", ".join(emitted_actions)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Interface Manifest",
        "",
        "This manifest describes the observed runtime interface for each active attack/defense agent.",
        "",
        f"Safety boundary: {SIMULATION_SAFETY_TEXT}",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row['agent']} ({row['side']})",
                "",
                f"- Goal: {row['goal']}",
                f"- Policies: {row['policies']}",
                f"- Input contract: {row['input_contract']}",
                f"- Memory contract: {row['memory_contract']}",
                f"- Tool contract: {row['tool_contract']}",
                f"- Candidate contract: {row['candidate_contract']}",
                f"- Selected action contract: {row['selected_action_contract']}",
                f"- Event outputs: {row['event_outputs']}",
                f"- Evidence experiments: {row['evidence_experiments']}",
                f"- Trace count: {row['trace_count']}",
                f"- Non-no-op decisions: {row['non_noop_count']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an observed AURA/TSRA-R interface manifest.")
    parser.add_argument(
        "--experiment-root",
        type=Path,
        default=Path("outputs/experiments"),
        help="Directory containing experiment subdirectories.",
    )
    parser.add_argument(
        "--experiments",
        nargs="*",
        default=DEFAULT_EXPERIMENTS,
        help="Experiment names to include.",
    )
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    traces = collect_traces(args.experiment_root, args.experiments)
    rows = build_manifest_rows(traces)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} agents)")
    print(f"Wrote {args.output_md} ({len(rows)} agents)")


if __name__ == "__main__":
    main()
