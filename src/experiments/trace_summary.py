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
]
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_decision_trace_summary.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_decision_trace_summary.md")

FIELDNAMES = [
    "experiment",
    "time_sec",
    "agent",
    "policy",
    "mission_phase",
    "active_link",
    "selected_action",
    "selected_event_ids",
    "score",
    "probability",
    "top_candidate",
    "top_candidate_signal",
    "reason",
    "tool_calls",
    "critical_pending",
    "total_queue_kb",
    "video_queue_kb",
    "stale_data_ratio",
    "priority_inversion_rate",
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


def summarize_trace(experiment: str, trace: dict[str, Any]) -> dict[str, Any]:
    observation = trace.get("observation") or {}
    signals = observation.get("signals") or {}
    selected = summarize_selected_action(trace.get("selected_action") or {})
    top_candidate = summarize_top_candidate(trace.get("candidate_actions") or [])
    tool_calls = ", ".join(
        call.get("tool_name", "") for call in trace.get("tool_calls", []) if call.get("tool_name")
    )

    return {
        "experiment": experiment,
        "time_sec": format_float(trace.get("time_sec")),
        "agent": trace.get("agent", ""),
        "policy": trace.get("policy", ""),
        "mission_phase": observation.get("mission_phase", ""),
        "active_link": observation.get("active_link", ""),
        "selected_action": selected["action"],
        "selected_event_ids": selected["event_ids"],
        "score": first_non_empty(selected["score"], top_candidate["score"]),
        "probability": first_non_empty(selected["probability"], top_candidate["probability"]),
        "top_candidate": top_candidate["action"],
        "top_candidate_signal": top_candidate["signal"],
        "reason": trace.get("reason", ""),
        "tool_calls": tool_calls,
        "critical_pending": signals.get("critical_pending", ""),
        "total_queue_kb": format_float(signals.get("total_queue_kb")),
        "video_queue_kb": format_float(signals.get("video_queue_kb")),
        "stale_data_ratio": format_float(signals.get("stale_data_ratio")),
        "priority_inversion_rate": format_float(signals.get("priority_inversion_rate")),
    }


def summarize_selected_action(selected: dict[str, Any]) -> dict[str, str]:
    action_type = selected.get("type", "unknown")
    if action_type == "attack_event":
        return {
            "action": selected.get("attack_type", "attack_event"),
            "event_ids": selected.get("event_id", ""),
            "score": format_float(selected.get("score")),
            "probability": "",
        }
    if action_type == "defense_events":
        events = selected.get("events") or []
        actions = [event.get("action", "") for event in events if event.get("action")]
        event_ids = [event.get("event_id", "") for event in events if event.get("event_id")]
        probability = first_probability_from_events(events)
        return {
            "action": "+".join(actions) if actions else "defense_events",
            "event_ids": "+".join(event_ids),
            "score": "",
            "probability": format_float(probability),
        }
    if action_type == "no_op":
        return {"action": "no_op", "event_ids": "", "score": "", "probability": ""}
    return {"action": str(action_type), "event_ids": "", "score": "", "probability": ""}


def summarize_top_candidate(candidates: list[dict[str, Any]]) -> dict[str, str]:
    if not candidates:
        return {"action": "", "score": "", "probability": "", "signal": ""}

    scored = [candidate for candidate in candidates if "score" in candidate]
    if scored:
        best = max(scored, key=lambda item: float(item.get("score") or 0.0))
        return {
            "action": str(best.get("action", "")),
            "score": format_float(best.get("score")),
            "probability": "",
            "signal": f"impact={format_float(best.get('predicted_mission_impact'))}; "
            f"detectability={format_float(best.get('detectability_score'))}",
        }

    probabilistic = [candidate for candidate in candidates if "probability" in candidate]
    if probabilistic:
        best = max(probabilistic, key=lambda item: float(item.get("probability") or 0.0))
        return {
            "action": str(best.get("action", "")),
            "score": "",
            "probability": format_float(best.get("probability")),
            "signal": f"eligible={best.get('eligible')}; threshold={format_float(best.get('threshold'))}; "
            f"active_until={format_float(best.get('active_defense_until'))}",
        }

    eligible_ready = [
        candidate
        for candidate in candidates
        if candidate.get("eligible") is True and candidate.get("ready") is True
    ]
    eligible = [candidate for candidate in candidates if candidate.get("eligible") is True]
    best = (eligible_ready or eligible or candidates)[0]
    return {
        "action": str(best.get("action", "")),
        "score": "",
        "probability": "",
        "signal": f"eligible={best.get('eligible')}; ready={best.get('ready')}",
    }


def first_probability_from_events(events: list[dict[str, Any]]) -> Any:
    for event in events:
        details = event.get("details") or {}
        if "probability" in details:
            return details["probability"]
    return ""


def first_non_empty(*values: Any) -> str:
    for value in values:
        if value not in ("", None):
            return format_float(value)
    return ""


def format_float(value: Any) -> str:
    if value in ("", None):
        return ""
    if isinstance(value, bool):
        return str(value)
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


def collect_rows(experiment_root: Path, experiments: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for experiment in experiments:
        for trace_filename in TRACE_FILES:
            path = experiment_root / experiment / trace_filename
            for trace in load_jsonl(path):
                rows.append(summarize_trace(experiment, trace))
    return sorted(rows, key=lambda row: (row["experiment"], float(row["time_sec"] or 0), row["agent"]))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    visible_fields = [
        "experiment",
        "time_sec",
        "agent",
        "policy",
        "selected_action",
        "score",
        "probability",
        "top_candidate",
        "top_candidate_signal",
        "reason",
    ]
    lines = [
        "# Agent Decision Trace Summary",
        "",
        "This table is generated from AURA and TSRA-R DecisionTrace JSONL logs.",
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
    text = str(value).replace("\n", " ").replace("|", "\\|")
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize agent DecisionTrace JSONL logs.")
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
