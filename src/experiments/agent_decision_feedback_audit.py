from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_EXPERIMENT_ROOT = Path("outputs/experiments")
DEFAULT_EPISODES = Path("outputs/report_tables/closed_loop_episode_replay.csv")
DEFAULT_LEDGER = Path("outputs/report_tables/defense_effectiveness_ledger.csv")
DEFAULT_ATTRIBUTION = Path("outputs/report_tables/defense_action_attribution_audit.csv")
DEFAULT_OUTPUT_CSV = Path("outputs/report_tables/agent_decision_feedback_audit.csv")
DEFAULT_OUTPUT_MD = Path("outputs/report_tables/agent_decision_feedback_audit.md")

CLOSED_LOOP_EXPERIMENTS = ("E5_rule_aura_tsra_r", "E7_ml_aura_ml_tsra_r")

SAFETY_BOUNDARY = (
    "closed simulation decision-feedback audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "experiment",
    "trace_id",
    "time_sec",
    "agent",
    "policy",
    "selected_event_id",
    "selected_event_type",
    "action",
    "decision_signal",
    "event_link_status",
    "metric_feedback_signal",
    "attribution_or_outcome_signal",
    "feedback_class",
    "feedback_status",
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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def collect_rows(
    *,
    experiment_root: Path = DEFAULT_EXPERIMENT_ROOT,
    episodes_path: Path = DEFAULT_EPISODES,
    ledger_path: Path = DEFAULT_LEDGER,
    attribution_path: Path = DEFAULT_ATTRIBUTION,
) -> list[dict[str, str]]:
    episode_by_attack = {
        (row.get("experiment", ""), row.get("attack_event_id", "")): row
        for row in read_csv(episodes_path)
    }
    ledger_by_event = {
        (row.get("experiment", ""), row.get("event_id", "")): row
        for row in read_csv(ledger_path)
    }
    attribution_by_action = {
        row.get("action", ""): row
        for row in read_csv(attribution_path)
        if row.get("action")
    }

    rows: list[dict[str, str]] = []
    for experiment in CLOSED_LOOP_EXPERIMENTS:
        exp_dir = experiment_root / experiment
        metrics = sorted(
            read_jsonl(exp_dir / "metric_snapshots.jsonl"),
            key=lambda row: as_float(row.get("time_sec")),
        )
        attacks = {
            row.get("event_id", ""): row
            for row in read_jsonl(exp_dir / "attack_events.jsonl")
        }
        defenses = {
            row.get("event_id", ""): row
            for row in read_jsonl(exp_dir / "defense_events.jsonl")
        }
        for trace in read_jsonl(exp_dir / "aura_decision_traces.jsonl"):
            selected = trace.get("selected_action") or {}
            if selected.get("type") == "attack_event":
                rows.append(
                    audit_attack_event(
                        experiment=experiment,
                        trace=trace,
                        attacks=attacks,
                        metrics=metrics,
                        episode_by_attack=episode_by_attack,
                    )
                )
        for trace in read_jsonl(exp_dir / "tsra_r_decision_traces.jsonl"):
            selected = trace.get("selected_action") or {}
            if selected.get("type") == "defense_events":
                for event in selected.get("events") or []:
                    rows.append(
                        audit_defense_event(
                            experiment=experiment,
                            trace=trace,
                            selected_event=event,
                            defenses=defenses,
                            metrics=metrics,
                            ledger_by_event=ledger_by_event,
                            attribution_by_action=attribution_by_action,
                        )
                    )

    return sorted(
        rows,
        key=lambda row: (
            row["experiment"],
            as_float(row["time_sec"]),
            row["agent"],
            row["trace_id"],
            row["selected_event_id"],
        ),
    )


def audit_attack_event(
    *,
    experiment: str,
    trace: dict[str, Any],
    attacks: dict[str, dict[str, Any]],
    metrics: list[dict[str, Any]],
    episode_by_attack: dict[tuple[str, str], dict[str, str]],
) -> dict[str, str]:
    selected = trace.get("selected_action") or {}
    event_id = str(selected.get("event_id") or "")
    event = attacks.get(event_id)
    issues: list[str] = []
    if not event:
        issues.append("selected attack event missing from attack_events log")
        return base_row(
            experiment=experiment,
            trace=trace,
            event_id=event_id,
            event_type="attack_event",
            action=str(selected.get("attack_type") or ""),
            decision_signal=attack_decision_signal(selected, event),
            event_link_status="missing_event",
            metric_feedback_signal="missing",
            attribution_or_outcome_signal="missing",
            feedback_class="missing_event",
            issues=issues,
        )

    candidate = event.get("candidate") or {}
    start_time = as_float(event.get("selected_at", selected.get("time_sec")))
    duration = as_float(candidate.get("duration_sec"), default=60.0)
    metric_summary = summarize_metrics(metrics, start_time, start_time + duration)
    episode = episode_by_attack.get((experiment, event_id), {})
    expected = as_float((event.get("expected_impact") or {}).get("mission_impact"))
    score = as_float(event.get("score", selected.get("score")))

    if not metric_summary["has_window"]:
        issues.append("no metric snapshots in attack feedback window")
    if expected <= 0.0:
        issues.append("attack event has no positive expected mission impact")

    before = metric_summary["before_mission_impact"]
    peak = metric_summary["peak_mission_impact"]
    after = metric_summary["after_mission_impact"]
    reduction = as_float(episode.get("impact_reduction_from_peak"))
    response_complete = episode.get("response_status") == "complete"

    if peak > before + 0.01 or after > before + 0.01:
        feedback_class = "attack_pressure_observed"
    elif response_complete and reduction > 0.0:
        feedback_class = "attack_contained_by_defense"
    else:
        feedback_class = "attack_feedback_present"

    status = "pass" if not issues else "fail"
    outcome_signal = (
        f"response={episode.get('response_status', '')}; "
        f"outcome={episode.get('outcome', '')}; "
        f"reduction_from_peak={episode.get('impact_reduction_from_peak', '')}"
    )
    return base_row(
        experiment=experiment,
        trace=trace,
        event_id=event_id,
        event_type="attack_event",
        action=str(candidate.get("attack_type") or selected.get("attack_type") or ""),
        decision_signal=(
            f"score={fmt(score)}; expected_mission_impact={fmt(expected)}; "
            f"target={candidate.get('target_link', selected.get('target_link', ''))}; "
            f"reason={event.get('reason', trace.get('reason', ''))}"
        ),
        event_link_status="linked",
        metric_feedback_signal=render_metric_summary(metric_summary),
        attribution_or_outcome_signal=outcome_signal,
        feedback_class=feedback_class,
        issues=issues,
        status=status,
    )


def audit_defense_event(
    *,
    experiment: str,
    trace: dict[str, Any],
    selected_event: dict[str, Any],
    defenses: dict[str, dict[str, Any]],
    metrics: list[dict[str, Any]],
    ledger_by_event: dict[tuple[str, str], dict[str, str]],
    attribution_by_action: dict[str, dict[str, str]],
) -> dict[str, str]:
    event_id = str(selected_event.get("event_id") or "")
    event = defenses.get(event_id)
    action = str(selected_event.get("action") or (event or {}).get("action") or "")
    issues: list[str] = []
    if not event:
        issues.append("selected defense event missing from defense_events log")
        return base_row(
            experiment=experiment,
            trace=trace,
            event_id=event_id,
            event_type="defense_event",
            action=action,
            decision_signal=defense_decision_signal(trace, action),
            event_link_status="missing_event",
            metric_feedback_signal="missing",
            attribution_or_outcome_signal="missing",
            feedback_class="missing_event",
            issues=issues,
        )

    event_time = as_float(event.get("time_sec", trace.get("time_sec")))
    ledger = ledger_by_event.get((experiment, event_id), {})
    attribution = attribution_by_action.get(action, {})
    if ledger:
        metric_signal = render_ledger_metric_signal(ledger)
        observed_effect = ledger.get("observed_effect", "")
    else:
        metric_summary = summarize_metrics(metrics, event_time, event_time + 30.0)
        metric_signal = render_metric_summary(metric_summary)
        observed_effect = "metric_window_present" if metric_summary["has_window"] else "missing_metric_window"
        issues.append("defense event missing from effectiveness ledger")

    attribution_status = attribution.get("attribution_status", "")
    attribution_class = attribution.get("attribution_class", "")
    if observed_effect == "improved":
        feedback_class = "defense_improved"
    elif observed_effect == "held":
        feedback_class = "defense_held"
    elif action == "ml_attack_alert" and attribution_status == "pass":
        feedback_class = "ml_window_triggered"
    elif attribution_status == "pass":
        feedback_class = "defense_bounded_or_lagged"
    else:
        feedback_class = "defense_unattributed"
        issues.append("defense feedback is neither improved/held nor attribution-supported")

    status = "pass" if not issues else "fail"
    attribution_signal = (
        f"observed_effect={observed_effect}; "
        f"attribution_class={attribution_class}; "
        f"attribution_status={attribution_status}; "
        f"primary_metric={attribution.get('primary_metric', '')}"
    )
    return base_row(
        experiment=experiment,
        trace=trace,
        event_id=event_id,
        event_type="defense_event",
        action=action,
        decision_signal=defense_decision_signal(trace, action),
        event_link_status="linked",
        metric_feedback_signal=metric_signal,
        attribution_or_outcome_signal=attribution_signal,
        feedback_class=feedback_class,
        issues=issues,
        status=status,
    )


def base_row(
    *,
    experiment: str,
    trace: dict[str, Any],
    event_id: str,
    event_type: str,
    action: str,
    decision_signal: str,
    event_link_status: str,
    metric_feedback_signal: str,
    attribution_or_outcome_signal: str,
    feedback_class: str,
    issues: list[str],
    status: str | None = None,
) -> dict[str, str]:
    feedback_status = status or ("pass" if not issues else "fail")
    return {
        "experiment": experiment,
        "trace_id": str(trace.get("trace_id") or ""),
        "time_sec": fmt(trace.get("time_sec")),
        "agent": str(trace.get("agent") or ""),
        "policy": str(trace.get("policy") or ""),
        "selected_event_id": event_id,
        "selected_event_type": event_type,
        "action": action,
        "decision_signal": decision_signal,
        "event_link_status": event_link_status,
        "metric_feedback_signal": metric_feedback_signal,
        "attribution_or_outcome_signal": attribution_or_outcome_signal,
        "feedback_class": feedback_class,
        "feedback_status": feedback_status,
        "issues": " || ".join(issues),
        "safety_boundary": SAFETY_BOUNDARY,
    }


def attack_decision_signal(selected: dict[str, Any], event: dict[str, Any] | None) -> str:
    if event:
        expected = (event.get("expected_impact") or {}).get("mission_impact")
        candidate = event.get("candidate") or {}
        return (
            f"score={fmt(event.get('score'))}; expected_mission_impact={fmt(expected)}; "
            f"target={candidate.get('target_link', '')}; reason={event.get('reason', '')}"
        )
    return (
        f"score={fmt(selected.get('score'))}; "
        f"target={selected.get('target_link', '')}; reason=selected attack event missing"
    )


def defense_decision_signal(trace: dict[str, Any], action: str) -> str:
    candidates = trace.get("candidate_actions") or []
    for candidate in candidates:
        if candidate.get("action") == action:
            return (
                f"eligible={candidate.get('eligible', '')}; ready={candidate.get('ready', '')}; "
                f"enabled={candidate.get('enabled', '')}; reason={candidate.get('reason', '')}"
            )
    if action == "ml_attack_alert":
        candidate = next(
            (item for item in candidates if item.get("action") == "open_defense_window"),
            {},
        )
        feedback = trace.get("feedback") or {}
        return (
            f"probability={fmt(candidate.get('probability', feedback.get('probability')))}; "
            f"threshold={fmt(candidate.get('threshold', feedback.get('threshold')))}; "
            f"active_defense_until={fmt(candidate.get('active_defense_until', feedback.get('active_defense_until')))}"
        )
    return f"reason={trace.get('reason', '')}"


def summarize_metrics(
    metrics: list[dict[str, Any]],
    start_time: float,
    end_time: float,
) -> dict[str, Any]:
    if not metrics:
        return {"has_window": False}
    window = [
        metric
        for metric in metrics
        if start_time <= as_float(metric.get("time_sec")) <= end_time
    ]
    before = metric_at_or_before(metrics, start_time)
    after = metric_at_or_before(metrics, end_time)
    if not window:
        window = [before, after]
    return {
        "has_window": bool(window and before and after),
        "before_time_sec": as_float(before.get("time_sec")),
        "after_time_sec": as_float(after.get("time_sec")),
        "before_mission_impact": as_float(before.get("mission_impact")),
        "peak_mission_impact": max(as_float(row.get("mission_impact")) for row in window),
        "after_mission_impact": as_float(after.get("mission_impact")),
        "peak_p95_critical_latency_sec": max(
            as_float(row.get("p95_critical_latency_sec")) for row in window
        ),
        "peak_trusted_stale_exposure": max(
            as_float(row.get("trusted_stale_exposure")) for row in window
        ),
        "peak_priority_inversion_rate": max(
            as_float(row.get("priority_inversion_rate")) for row in window
        ),
    }


def metric_at_or_before(metrics: list[dict[str, Any]], time_sec: float) -> dict[str, Any]:
    previous = [row for row in metrics if as_float(row.get("time_sec")) <= time_sec]
    if previous:
        return max(previous, key=lambda row: as_float(row.get("time_sec")))
    return metrics[0]


def render_metric_summary(summary: dict[str, Any]) -> str:
    if not summary.get("has_window"):
        return "missing"
    delta = summary["after_mission_impact"] - summary["before_mission_impact"]
    return (
        f"before={fmt(summary['before_mission_impact'])}@t={fmt(summary['before_time_sec'])}; "
        f"peak={fmt(summary['peak_mission_impact'])}; "
        f"after={fmt(summary['after_mission_impact'])}@t={fmt(summary['after_time_sec'])}; "
        f"delta={fmt(delta)}; "
        f"peak_latency={fmt(summary['peak_p95_critical_latency_sec'])}; "
        f"peak_trusted_stale={fmt(summary['peak_trusted_stale_exposure'])}; "
        f"peak_priority_inversion={fmt(summary['peak_priority_inversion_rate'])}"
    )


def render_ledger_metric_signal(ledger: dict[str, str]) -> str:
    return (
        f"before={ledger.get('before_mission_impact', '')}; "
        f"after={ledger.get('after_mission_impact', '')}; "
        f"delta={ledger.get('delta_mission_impact', '')}; "
        f"latency_delta={ledger.get('delta_p95_critical_latency_sec', '')}; "
        f"trusted_stale_delta={ledger.get('delta_trusted_stale_exposure', '')}; "
        f"priority_delta={ledger.get('delta_priority_inversion_rate', '')}"
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Decision Feedback Audit",
        "",
        "This audit links selected DecisionTrace events in the defended E5/E7 closed-loop runs to event logs, metric feedback, closed-loop outcomes, and defense action attribution.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "## Summary",
        "",
        f"- Feedback rows: {len(rows)}",
        f"- Status counts: {format_counts(count_values(rows, 'feedback_status'))}",
        f"- Event type counts: {format_counts(count_values(rows, 'selected_event_type'))}",
        f"- Feedback classes: {format_counts(count_values(rows, 'feedback_class'))}",
        "",
        "## Review Table",
        "",
    ]
    visible_fields = [
        "experiment",
        "trace_id",
        "selected_event_id",
        "selected_event_type",
        "action",
        "feedback_class",
        "feedback_status",
    ]
    lines.append(markdown_row(visible_fields))
    lines.append(markdown_row(["---"] * len(visible_fields)))
    for row in rows:
        lines.append(markdown_row([markdown_cell(row[field]) for field in visible_fields]))
    lines.extend(["", "## Detail", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['experiment']} {row['trace_id']} {row['selected_event_id']}",
                "",
                f"- Agent: {row['agent']} policy={row['policy']}",
                f"- Decision: {row['decision_signal']}",
                f"- Event link: {row['event_link_status']}",
                f"- Metrics: {row['metric_feedback_signal']}",
                f"- Attribution/outcome: {row['attribution_or_outcome_signal']}",
                f"- Class: {row['feedback_class']}",
                f"- Status: {row['feedback_status']}",
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
    parser = argparse.ArgumentParser(description="Audit post-decision feedback for selected agent events.")
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--episodes", type=Path, default=DEFAULT_EPISODES)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--attribution", type=Path, default=DEFAULT_ATTRIBUTION)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any selected event lacks feedback evidence.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_rows(
        experiment_root=args.experiment_root,
        episodes_path=args.episodes,
        ledger_path=args.ledger,
        attribution_path=args.attribution,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [row for row in rows if row["feedback_status"] != "pass"]
    print(f"Wrote {args.output_csv} ({len(rows)} rows)")
    print(f"Wrote {args.output_md} ({len(rows)} rows)")
    if failed:
        print(f"Failed feedback rows: {', '.join(row['selected_event_id'] for row in failed[:12])}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
