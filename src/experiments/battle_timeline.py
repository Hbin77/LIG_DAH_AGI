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
]
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/battle_timeline.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/battle_timeline.md")

FIELDNAMES = [
    "experiment",
    "time_sec",
    "mission_phase",
    "active_link",
    "attack_events",
    "defense_events",
    "aura_decision",
    "tsra_r_decision",
    "mission_impact",
    "p95_critical_latency_sec",
    "trusted_stale_exposure",
    "priority_inversion_rate",
    "stale_data_ratio",
    "critical_pending",
    "video_queue_kb",
    "total_queue_kb",
    "safety_boundary",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def time_key(value: Any) -> float:
    try:
        return round(float(value), 6)
    except (TypeError, ValueError):
        return 0.0


def collect_rows(experiment_root: Path, experiments: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for experiment in experiments:
        exp_dir = experiment_root / experiment
        attacks = load_jsonl(exp_dir / "attack_events.jsonl")
        defenses = load_jsonl(exp_dir / "defense_events.jsonl")
        metrics = load_jsonl(exp_dir / "metric_snapshots.jsonl")
        traces = []
        for trace_file in TRACE_FILES:
            traces.extend(load_jsonl(exp_dir / trace_file))

        event_times = sorted(
            {
                time_key(attack.get("selected_at"))
                for attack in attacks
            }
            | {
                time_key(defense.get("time_sec"))
                for defense in defenses
            }
        )

        attacks_by_time = group_by_time(attacks, "selected_at")
        defenses_by_time = group_by_time(defenses, "time_sec")
        traces_by_time = group_by_time(traces, "time_sec")
        metrics_by_time = {time_key(metric.get("time_sec")): metric for metric in metrics}

        for event_time in event_times:
            metric = nearest_metric(metrics_by_time, event_time)
            trace_set = traces_by_time.get(event_time, [])
            row = {
                "experiment": experiment,
                "time_sec": format_float(event_time),
                "mission_phase": first_observation_value(trace_set, "mission_phase"),
                "active_link": first_observation_value(trace_set, "active_link"),
                "attack_events": summarize_attacks(attacks_by_time.get(event_time, [])),
                "defense_events": summarize_defenses(defenses_by_time.get(event_time, [])),
                "aura_decision": summarize_agent_decisions(trace_set, "AURA"),
                "tsra_r_decision": summarize_agent_decisions(trace_set, "TSRA-R"),
                "mission_impact": format_float(metric.get("mission_impact")),
                "p95_critical_latency_sec": format_float(
                    metric.get("p95_critical_latency_sec")
                ),
                "trusted_stale_exposure": format_float(
                    metric.get("trusted_stale_exposure")
                ),
                "priority_inversion_rate": format_float(
                    metric.get("priority_inversion_rate")
                ),
                "stale_data_ratio": format_float(metric.get("stale_data_ratio")),
                "critical_pending": first_signal_value(trace_set, "critical_pending"),
                "video_queue_kb": first_signal_value(trace_set, "video_queue_kb"),
                "total_queue_kb": first_signal_value(trace_set, "total_queue_kb"),
                "safety_boundary": "closed simulation event only; no RF, exploit, or live network action",
            }
            rows.append(row)
    return rows


def group_by_time(rows: list[dict[str, Any]], time_field: str) -> dict[float, list[dict[str, Any]]]:
    grouped: dict[float, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(time_key(row.get(time_field)), []).append(row)
    return grouped


def nearest_metric(metrics_by_time: dict[float, dict[str, Any]], event_time: float) -> dict[str, Any]:
    if event_time in metrics_by_time:
        return metrics_by_time[event_time]
    prior_times = [time for time in metrics_by_time if time <= event_time]
    if prior_times:
        return metrics_by_time[max(prior_times)]
    if metrics_by_time:
        return metrics_by_time[min(metrics_by_time)]
    return {}


def summarize_attacks(attacks: list[dict[str, Any]]) -> str:
    parts = []
    for attack in attacks:
        candidate = attack.get("candidate") or {}
        traffic = ",".join(candidate.get("target_traffic_classes") or [])
        expected = attack.get("expected_impact") or {}
        parts.append(
            compact(
                [
                    attack.get("event_id", ""),
                    candidate.get("attack_type", ""),
                    f"target={candidate.get('target_link', '')}",
                    f"traffic={traffic}",
                    f"score={format_float(attack.get('score'))}",
                    f"expected_impact={format_float(expected.get('mission_impact'))}",
                    f"reason={attack.get('reason', candidate.get('reason', ''))}",
                ]
            )
        )
    return " || ".join(parts)


def summarize_defenses(defenses: list[dict[str, Any]]) -> str:
    parts = []
    for defense in defenses:
        details = defense.get("details") or {}
        detail_parts = []
        if "target_link" in details:
            detail_parts.append(f"target={details.get('target_link')}")
        if "probability" in details:
            detail_parts.append(f"probability={format_float(details.get('probability'))}")
        if "threshold" in details:
            detail_parts.append(f"threshold={format_float(details.get('threshold'))}")
        if "until_sec" in details:
            detail_parts.append(f"until={format_float(details.get('until_sec'))}")
        if "reason" in details:
            detail_parts.append(f"reason={details.get('reason')}")
        parts.append(
            compact(
                [
                    defense.get("event_id", ""),
                    defense.get("action", ""),
                    *detail_parts,
                ]
            )
        )
    return " || ".join(parts)


def summarize_agent_decisions(traces: list[dict[str, Any]], agent_prefix: str) -> str:
    parts = []
    for trace in traces:
        agent = trace.get("agent", "")
        if not agent.startswith(agent_prefix):
            continue
        selected = summarize_selected_action(trace.get("selected_action") or {})
        tool_names = [
            call.get("tool_name", "")
            for call in trace.get("tool_calls", [])
            if call.get("tool_name")
        ]
        top_candidate = summarize_top_candidate(trace.get("candidate_actions") or [])
        feedback = summarize_feedback(trace.get("feedback") or {})
        parts.append(
            compact(
                [
                    agent,
                    trace.get("policy", ""),
                    f"selected={selected}",
                    f"top={top_candidate}" if top_candidate else "",
                    f"tools={summarize_tool_names(tool_names)}" if tool_names else "",
                    f"feedback={feedback}" if feedback else "",
                    f"reason={trace.get('reason', '')}",
                ]
            )
        )
    return " || ".join(parts)


def summarize_tool_names(tool_names: list[str]) -> str:
    counts: dict[str, int] = {}
    ordered = []
    for name in tool_names:
        if name not in counts:
            counts[name] = 0
            ordered.append(name)
        counts[name] += 1
    return "+".join(
        name if counts[name] == 1 else f"{name}x{counts[name]}" for name in ordered
    )


def summarize_selected_action(selected: dict[str, Any]) -> str:
    action_type = selected.get("type", "unknown")
    if action_type == "attack_event":
        return compact(
            [
                selected.get("event_id", ""),
                selected.get("attack_type", "attack_event"),
                f"score={format_float(selected.get('score'))}",
            ]
        )
    if action_type == "defense_events":
        events = selected.get("events") or []
        actions = [
            compact([event.get("event_id", ""), event.get("action", "")])
            for event in events
        ]
        return "+".join(action for action in actions if action)
    if action_type == "no_op":
        return "no_op"
    return str(action_type)


def summarize_top_candidate(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return ""
    scored = [candidate for candidate in candidates if "score" in candidate]
    if scored:
        best = max(scored, key=lambda item: float(item.get("score") or 0.0))
        return compact(
            [
                best.get("action", ""),
                f"score={format_float(best.get('score'))}",
                f"impact={format_float(best.get('predicted_mission_impact'))}",
                f"detect={format_float(best.get('detectability_score'))}",
            ]
        )
    probabilistic = [candidate for candidate in candidates if "probability" in candidate]
    if probabilistic:
        best = max(probabilistic, key=lambda item: float(item.get("probability") or 0.0))
        return compact(
            [
                best.get("action", ""),
                f"probability={format_float(best.get('probability'))}",
                f"threshold={format_float(best.get('threshold'))}",
                f"eligible={best.get('eligible')}",
            ]
        )
    eligible_ready = [
        candidate
        for candidate in candidates
        if candidate.get("eligible") is True and candidate.get("ready") is True
    ]
    eligible = [candidate for candidate in candidates if candidate.get("eligible") is True]
    best = (eligible_ready or eligible or candidates)[0]
    return compact(
        [
            best.get("action", ""),
            f"eligible={best.get('eligible')}",
            f"ready={best.get('ready')}",
        ]
    )


def summarize_feedback(feedback: dict[str, Any]) -> str:
    if "probability" in feedback:
        return compact(
            [
                f"probability={format_float(feedback.get('probability'))}",
                f"threshold={format_float(feedback.get('threshold'))}",
                f"opened_window={feedback.get('opened_window')}",
            ]
        )
    if "event_count" in feedback or "enabled_actions" in feedback:
        enabled = feedback.get("enabled_actions")
        enabled_text = ",".join(enabled) if isinstance(enabled, list) else ""
        return compact(
            [
                f"events={feedback.get('event_count')}",
                f"enabled={enabled_text}" if enabled_text else "",
            ]
        )
    return ""


def first_observation_value(traces: list[dict[str, Any]], key: str) -> str:
    for trace in traces:
        observation = trace.get("observation") or {}
        value = observation.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def first_signal_value(traces: list[dict[str, Any]], key: str) -> str:
    for trace in traces:
        signals = (trace.get("observation") or {}).get("signals") or {}
        value = signals.get(key)
        if value not in (None, ""):
            return format_float(value)
    return ""


def compact(parts: list[Any]) -> str:
    return "; ".join(str(part) for part in parts if part not in ("", None))


def format_float(value: Any) -> str:
    if value in ("", None):
        return ""
    if isinstance(value, bool):
        return str(value)
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
    visible_fields = [
        "experiment",
        "time_sec",
        "attack_events",
        "defense_events",
        "aura_decision",
        "tsra_r_decision",
        "mission_impact",
        "trusted_stale_exposure",
        "priority_inversion_rate",
    ]
    lines = [
        "# AURA / TSRA-R Battle Timeline",
        "",
        "This table merges attack events, defense events, DecisionTrace reasons, and metric snapshots on the same event timeline.",
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
    parser = argparse.ArgumentParser(
        description="Merge attack events, defense events, traces, and metrics into one battle timeline."
    )
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
        help="Experiment names to summarize.",
    )
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.experiment_root, args.experiments)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"Wrote {args.output_csv} ({len(rows)} rows)")
    print(f"Wrote {args.output_md} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
