from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENTS = [
    "E5_rule_aura_tsra_r",
    "E7_ml_aura_ml_tsra_r",
]
TRACE_FILES = [
    "aura_decision_traces.jsonl",
    "tsra_r_decision_traces.jsonl",
    "tsra_r_rule_delegate_traces.jsonl",
]
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_loop_replay.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_loop_replay.md")

FIELDNAMES = [
    "experiment",
    "agent",
    "policy",
    "trace_file",
    "trace_id",
    "time_sec",
    "loop_case",
    "observe",
    "memory",
    "tools",
    "candidates",
    "selected_action",
    "feedback",
    "reason",
    "safety_boundary",
]

SIMULATION_SAFETY_TEXT = (
    "closed simulation agent-loop replay only; no RF, exploit, or live network action"
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


def collect_rows(experiment_root: Path, experiments: list[str]) -> list[dict[str, str]]:
    replay_rows: list[dict[str, str]] = []
    for experiment in experiments:
        traces = []
        exp_dir = experiment_root / experiment
        for filename in TRACE_FILES:
            for trace in read_jsonl(exp_dir / filename):
                trace["_trace_file"] = filename
                traces.append(trace)
        grouped = group_by_agent_policy(traces)
        for (agent, policy), group in sorted(grouped.items()):
            for loop_case, trace in representative_traces(group):
                replay_rows.append(summarize_trace(experiment, loop_case, trace))
    return replay_rows


def group_by_agent_policy(
    traces: list[dict[str, Any]],
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for trace in traces:
        key = (str(trace.get("agent", "")), str(trace.get("policy", "")))
        grouped.setdefault(key, []).append(trace)
    for key in grouped:
        grouped[key] = sorted(grouped[key], key=lambda row: as_float(row.get("time_sec")))
    return grouped


def representative_traces(group: list[dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    selected: list[tuple[str, dict[str, Any]]] = []
    no_op = next(
        (
            trace
            for trace in group
            if (trace.get("selected_action") or {}).get("type") == "no_op"
        ),
        None,
    )
    action = next(
        (
            trace
            for trace in group
            if (trace.get("selected_action") or {}).get("type") not in ("", None, "no_op")
        ),
        None,
    )
    if no_op:
        selected.append(("no_op", no_op))
    if action:
        selected.append(("action", action))
    return selected


def summarize_trace(experiment: str, loop_case: str, trace: dict[str, Any]) -> dict[str, str]:
    return {
        "experiment": experiment,
        "agent": str(trace.get("agent", "")),
        "policy": str(trace.get("policy", "")),
        "trace_file": str(trace.get("_trace_file", "")),
        "trace_id": str(trace.get("trace_id", "")),
        "time_sec": format_value(trace.get("time_sec")),
        "loop_case": loop_case,
        "observe": summarize_observation(trace.get("observation") or {}),
        "memory": summarize_memory(trace.get("memory") or {}),
        "tools": summarize_tools(trace.get("tool_calls") or []),
        "candidates": summarize_candidates(trace.get("candidate_actions") or []),
        "selected_action": summarize_selected_action(trace.get("selected_action") or {}),
        "feedback": summarize_feedback(trace.get("feedback") or {}),
        "reason": str(trace.get("reason", "")),
        "safety_boundary": SIMULATION_SAFETY_TEXT,
    }


def summarize_observation(observation: dict[str, Any]) -> str:
    signals = observation.get("signals") or {}
    parts = [
        f"phase={observation.get('mission_phase', '')}",
        f"active_link={observation.get('active_link', '')}",
        f"critical_pending={signals.get('critical_pending', '')}",
        f"queue_kb={format_value(signals.get('total_queue_kb'))}",
        f"video_kb={format_value(signals.get('video_queue_kb'))}",
        f"stale={format_value(signals.get('stale_data_ratio'))}",
        f"priority_inversion={format_value(signals.get('priority_inversion_rate'))}",
    ]
    return compact(parts)


def summarize_memory(memory: dict[str, Any]) -> str:
    belief = memory.get("belief_state") or {}
    last_selected = memory.get("last_selected_action") or {}
    belief_parts = []
    for key in [
        "mode",
        "event_count",
        "last_attack_type",
        "last_probability",
        "active_defense_until",
        "enabled_actions",
        "adaptive_policy",
    ]:
        if key in belief:
            belief_parts.append(f"{key}={format_value(belief.get(key))}")
    parts = [
        f"observations={memory.get('observation_count', '')}",
        f"decisions={memory.get('decision_count', '')}",
        f"last_selected={last_selected.get('type', '')}",
        *belief_parts,
    ]
    return compact(parts)


def summarize_tools(tool_calls: list[dict[str, Any]]) -> str:
    if not tool_calls:
        return "none"
    counts: dict[str, int] = {}
    samples: dict[str, str] = {}
    order = []
    for call in tool_calls:
        name = str(call.get("tool_name", ""))
        if not name:
            continue
        if name not in counts:
            counts[name] = 0
            order.append(name)
            samples[name] = summarize_tool_output(call.get("output_summary"))
        counts[name] += 1
    return "; ".join(
        f"{name}x{counts[name]} -> {samples[name]}" if counts[name] > 1 else f"{name} -> {samples[name]}"
        for name in order
    )


def summarize_tool_output(output: Any) -> str:
    if isinstance(output, dict):
        interesting = []
        for key in [
            "candidate_count",
            "mission_impact",
            "detectability_score",
            "probability",
            "priority_reroute_needed",
            "stale_badge_needed",
            "pace_switch_needed",
            "video_throttle_needed",
        ]:
            if key in output:
                interesting.append(f"{key}={format_value(output.get(key))}")
        if interesting:
            return compact(interesting)
        return compact([f"{key}={format_value(value)}" for key, value in list(output.items())[:3]])
    if isinstance(output, list):
        return f"items={len(output)}"
    return format_value(output)


def summarize_candidates(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return "none"
    ranked = sorted(candidates, key=candidate_rank_score, reverse=True)
    top = ranked[:3]
    parts = []
    for candidate in top:
        action = candidate.get("action", "")
        if "score" in candidate:
            parts.append(
                compact(
                    [
                        str(action),
                        f"score={format_value(candidate.get('score'))}",
                        f"impact={format_value(candidate.get('predicted_mission_impact'))}",
                        f"detectability={format_value(candidate.get('detectability_score'))}",
                        f"target={candidate.get('target_link', '')}",
                    ]
                )
            )
        elif "probability" in candidate:
            parts.append(
                compact(
                    [
                        str(action),
                        f"probability={format_value(candidate.get('probability'))}",
                        f"threshold={format_value(candidate.get('threshold'))}",
                        f"eligible={candidate.get('eligible')}",
                    ]
                )
            )
        else:
            parts.append(
                compact(
                    [
                        str(action),
                        f"eligible={candidate.get('eligible')}",
                        f"ready={candidate.get('ready')}",
                        f"enabled={candidate.get('enabled')}",
                    ]
                )
            )
    suffix = f"; total={len(candidates)}"
    return " || ".join(parts) + suffix


def candidate_rank_score(candidate: dict[str, Any]) -> float:
    if "score" in candidate:
        return as_float(candidate.get("score"))
    if "probability" in candidate:
        return as_float(candidate.get("probability"))
    if candidate.get("eligible") is True and candidate.get("ready") is True:
        return 2.0
    if candidate.get("eligible") is True:
        return 1.0
    return 0.0


def summarize_selected_action(selected: dict[str, Any]) -> str:
    selected_type = selected.get("type", "")
    if selected_type == "attack_event":
        return compact(
            [
                "attack_event",
                selected.get("event_id", ""),
                selected.get("attack_type", ""),
                f"target={selected.get('target_link', '')}",
                f"score={format_value(selected.get('score'))}",
            ]
        )
    if selected_type == "defense_events":
        events = selected.get("events") or []
        actions = []
        for event in events:
            details = event.get("details") or {}
            actions.append(
                compact(
                    [
                        event.get("event_id", ""),
                        event.get("action", ""),
                        f"probability={format_value(details.get('probability'))}" if "probability" in details else "",
                        f"until={format_value(details.get('until_sec'))}" if "until_sec" in details else "",
                    ]
                )
            )
        return "defense_events: " + " + ".join(action for action in actions if action)
    if selected_type == "no_op":
        return "no_op"
    return str(selected_type or "unknown")


def summarize_feedback(feedback: dict[str, Any]) -> str:
    if not feedback:
        return "none"
    parts = []
    for key in [
        "attack_threshold",
        "cooldown_sec",
        "event_count",
        "mode",
        "enabled_actions",
        "last_probability",
        "active_defense_until",
        "adaptive_policy",
    ]:
        if key in feedback:
            parts.append(f"{key}={format_value(feedback.get(key))}")
    return compact(parts) if parts else compact(
        f"{key}={format_value(value)}" for key, value in list(feedback.items())[:4]
    )


def compact(parts: Any) -> str:
    return "; ".join(str(part) for part in parts if part not in ("", None, []))


def as_float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def format_value(value: Any) -> str:
    if value in ("", None):
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    if isinstance(value, dict):
        return ",".join(f"{key}:{format_value(val)}" for key, val in value.items())
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
        "# Agent Loop Replay",
        "",
        "This replay reconstructs representative observe-memory-tool-candidate-decision-feedback loops.",
        "",
        f"Safety boundary: {SIMULATION_SAFETY_TEXT}",
        "",
    ]
    for idx, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"## Replay-{idx:02d}: {row['experiment']} / {row['agent']} / {row['loop_case']}",
                "",
                f"- Policy: `{row['policy']}`",
                f"- Trace: `{row['trace_id']}` from `{row['trace_file']}` at t={row['time_sec']} sec",
                f"- Observe: {row['observe']}",
                f"- Memory: {row['memory']}",
                f"- Tools: {row['tools']}",
                f"- Candidates: {row['candidates']}",
                f"- Selected action: {row['selected_action']}",
                f"- Feedback: {row['feedback']}",
                f"- Reason: {row['reason']}",
                f"- Safety boundary: {row['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate representative AURA/TSRA-R agent loop replays.")
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
    rows = collect_rows(args.experiment_root, args.experiments)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} replay rows)")
    print(f"Wrote {args.output_md} ({len(rows)} replay rows)")


if __name__ == "__main__":
    main()
