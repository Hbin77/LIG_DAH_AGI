from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/reactive_defense_tradeoff_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/reactive_defense_tradeoff_audit.md"

E6 = "E6_ml_aura_tsra_r"
E7 = "E7_ml_aura_ml_tsra_r"
CORE_ACTIONS = {"pace_switch", "priority_reroute", "stale_badge", "video_throttle"}
SAFETY_BOUNDARY = (
    "closed simulation reactive-defense tradeoff audit only; no RF, exploit, or live network action"
)

FIELDNAMES = [
    "check_id",
    "area",
    "requirement",
    "evidence",
    "observed",
    "status",
    "interpretation",
    "safety_boundary",
]


def read_jsonl(rel: str) -> list[dict[str, Any]]:
    path = ROOT / rel
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_csv(rel: str) -> list[dict[str, str]]:
    path = ROOT / rel
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value: float) -> str:
    return f"{value:.6g}"


def row(
    *,
    check_id: str,
    area: str,
    requirement: str,
    evidence: list[str],
    observed: str,
    ok: bool,
    interpretation: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "requirement": requirement,
        "evidence": " | ".join(evidence),
        "observed": observed,
        "status": "pass" if ok else "fail",
        "interpretation": interpretation,
        "safety_boundary": SAFETY_BOUNDARY,
    }


def experiment_path(experiment: str, filename: str) -> str:
    return f"outputs/experiments/{experiment}/{filename}"


def attack_window(attack: dict[str, Any]) -> tuple[float, float, str]:
    candidate = attack.get("candidate") or {}
    start = as_float(attack.get("selected_at"))
    duration = as_float(candidate.get("duration_sec"))
    return start, start + duration, str(candidate.get("attack_type") or "")


def first_attack_time(attacks: list[dict[str, Any]]) -> float:
    if not attacks:
        return 0.0
    return min(as_float(attack.get("selected_at")) for attack in attacks)


def action_counts(defenses: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(defense.get("action") or "") for defense in defenses)


def core_action_count(defenses: list[dict[str, Any]]) -> int:
    return sum(1 for defense in defenses if defense.get("action") in CORE_ACTIONS)


def pre_first_attack_count(
    defenses: list[dict[str, Any]],
    first_attack_sec: float,
) -> int:
    return sum(1 for defense in defenses if as_float(defense.get("time_sec")) < first_attack_sec)


def first_event_latency_after(
    defenses: list[dict[str, Any]],
    first_attack_sec: float,
    action_filter: set[str] | None = None,
) -> float:
    matching = [
        as_float(defense.get("time_sec")) - first_attack_sec
        for defense in defenses
        if as_float(defense.get("time_sec")) >= first_attack_sec
        and (action_filter is None or defense.get("action") in action_filter)
    ]
    return min(matching) if matching else 0.0


def ml_alert_overlap_stats(
    alerts: list[dict[str, Any]],
    attacks: list[dict[str, Any]],
) -> tuple[int, int, float, float]:
    active_overlap = 0
    probabilities = []
    thresholds = []
    windows = [attack_window(attack) for attack in attacks]
    for alert in alerts:
        t = as_float(alert.get("time_sec"))
        details = alert.get("details") or {}
        probabilities.append(as_float(details.get("probability")))
        thresholds.append(as_float(details.get("threshold")))
        if any(start <= t <= end for start, end, _ in windows):
            active_overlap += 1
    avg_probability = sum(probabilities) / len(probabilities) if probabilities else 0.0
    threshold = max(thresholds) if thresholds else 0.0
    return len(alerts), active_overlap, avg_probability, threshold


def trace_probability_stats(traces: list[dict[str, Any]]) -> dict[str, float]:
    probabilities = []
    thresholds = []
    opened = 0
    no_op = 0
    for trace in traces:
        feedback = trace.get("feedback") or {}
        if "probability" in feedback:
            probabilities.append(as_float(feedback.get("probability")))
        if "threshold" in feedback:
            thresholds.append(as_float(feedback.get("threshold")))
        if feedback.get("opened_window"):
            opened += 1
        selected = trace.get("selected_action") or {}
        if selected.get("type") == "no_op":
            no_op += 1

    threshold = max(thresholds) if thresholds else 0.0
    below = sum(1 for value in probabilities if value < threshold)
    above = sum(1 for value in probabilities if value >= threshold)
    return {
        "trace_count": float(len(traces)),
        "probability_count": float(len(probabilities)),
        "threshold": threshold,
        "below_threshold": float(below),
        "above_threshold": float(above),
        "opened_window": float(opened),
        "no_op": float(no_op),
        "min_probability": min(probabilities) if probabilities else 0.0,
        "max_probability": max(probabilities) if probabilities else 0.0,
    }


def repeated_summary() -> dict[str, dict[str, str]]:
    return {
        row["experiment"]: row
        for row in read_csv("outputs/batch/repeated_experiment_summary.csv")
    }


def build_rows() -> list[dict[str, str]]:
    e6_attacks = read_jsonl(experiment_path(E6, "attack_events.jsonl"))
    e7_attacks = read_jsonl(experiment_path(E7, "attack_events.jsonl"))
    e6_defenses = read_jsonl(experiment_path(E6, "defense_events.jsonl"))
    e7_defenses = read_jsonl(experiment_path(E7, "defense_events.jsonl"))
    e6_traces = read_jsonl(experiment_path(E6, "tsra_r_decision_traces.jsonl"))
    e7_traces = read_jsonl(experiment_path(E7, "tsra_r_decision_traces.jsonl"))

    e6_first_attack = first_attack_time(e6_attacks)
    e7_first_attack = first_attack_time(e7_attacks)
    e6_pre_first = pre_first_attack_count(e6_defenses, e6_first_attack)
    e7_pre_first = pre_first_attack_count(e7_defenses, e7_first_attack)
    e6_first_core_latency = first_event_latency_after(
        e6_defenses,
        e6_first_attack,
        CORE_ACTIONS,
    )
    e7_first_alert_latency = first_event_latency_after(
        e7_defenses,
        e7_first_attack,
        {"ml_attack_alert"},
    )

    e6_actions = action_counts(e6_defenses)
    e7_actions = action_counts(e7_defenses)
    e7_alerts = [
        defense for defense in e7_defenses if defense.get("action") == "ml_attack_alert"
    ]
    alert_count, active_overlap, avg_probability, threshold = ml_alert_overlap_stats(
        e7_alerts,
        e7_attacks,
    )
    e7_trace_stats = trace_probability_stats(e7_traces)

    summaries = repeated_summary()
    e6_summary = summaries.get(E6, {})
    e7_summary = summaries.get(E7, {})
    e6_impact = as_float(e6_summary.get("mission_impact_mean"))
    e7_impact = as_float(e7_summary.get("mission_impact_mean"))
    e6_std = as_float(e6_summary.get("mission_impact_std"))
    e7_std = as_float(e7_summary.get("mission_impact_std"))
    impact_delta = e7_impact - e6_impact

    e6_policies = sorted({str(trace.get("policy") or "") for trace in e6_traces})
    e7_policies = sorted({str(trace.get("policy") or "") for trace in e7_traces})
    e7_core_actions = {action for action in e7_actions if action in CORE_ACTIONS}

    return [
        row(
            check_id="RDT01",
            area="Policy separation",
            requirement="E6 and E7 must represent different defense policies, not the same rule path.",
            evidence=[
                experiment_path(E6, "tsra_r_decision_traces.jsonl"),
                experiment_path(E7, "tsra_r_decision_traces.jsonl"),
            ],
            observed=(
                f"e6_policies={','.join(e6_policies)}; "
                f"e7_policies={','.join(e7_policies)}; "
                f"e6_trace_count={len(e6_traces)}; e7_trace_count={len(e7_traces)}"
            ),
            ok=e6_policies == ["rule_defense_full"]
            and e7_policies == ["ml_anomaly_detector"]
            and len(e6_traces) == len(e7_traces) == 61,
            interpretation=(
                "E6 is the always-on full rule defender; E7 is the ML anomaly detector "
                "that opens or refreshes reactive defense windows."
            ),
        ),
        row(
            check_id="RDT02",
            area="Pre-attack defense suppression",
            requirement="Reactive ML defense should avoid emitting defense events before the first observed AURA-ML attack.",
            evidence=[
                experiment_path(E6, "defense_events.jsonl"),
                experiment_path(E7, "defense_events.jsonl"),
                experiment_path(E7, "attack_events.jsonl"),
            ],
            observed=(
                f"first_attack_sec={fmt(e7_first_attack)}; "
                f"e6_pre_first_defense_events={e6_pre_first}; "
                f"e7_pre_first_defense_events={e7_pre_first}"
            ),
            ok=e6_pre_first > 0 and e7_pre_first == 0,
            interpretation=(
                "E7 removes the pre-attack stale-badge behavior seen in E6. This is a "
                "reactive-defense benefit, separate from mission-impact minimization."
            ),
        ),
        row(
            check_id="RDT03",
            area="First-response latency cost",
            requirement="Reactive gating must expose its first-response delay instead of hiding it.",
            evidence=[
                experiment_path(E6, "defense_events.jsonl"),
                experiment_path(E7, "defense_events.jsonl"),
            ],
            observed=(
                f"e6_first_core_response_latency_sec={fmt(e6_first_core_latency)}; "
                f"e7_first_ml_alert_latency_sec={fmt(e7_first_alert_latency)}"
            ),
            ok=0.0 < e7_first_alert_latency <= 25.0,
            interpretation=(
                "E7 waits for detector confidence before opening the defense window; the "
                "measured cost in the representative run is a 20 second first-alert delay."
            ),
        ),
        row(
            check_id="RDT04",
            area="ML alert attack overlap",
            requirement="ML alerts should occur during active simulated AURA-ML attack windows.",
            evidence=[
                experiment_path(E7, "attack_events.jsonl"),
                experiment_path(E7, "defense_events.jsonl"),
            ],
            observed=(
                f"ml_attack_alerts={alert_count}; active_attack_overlap={active_overlap}; "
                f"avg_alert_probability={fmt(avg_probability)}; threshold={fmt(threshold)}"
            ),
            ok=alert_count > 0 and active_overlap == alert_count and avg_probability >= threshold,
            interpretation=(
                "Every E7 ML alert overlaps an active simulated attack window, so the alert "
                "stream is tied to attack context rather than arbitrary noise."
            ),
        ),
        row(
            check_id="RDT05",
            area="Core defense preservation",
            requirement="Reactive ML TSRA-R must still emit the core TSRA-R actions after detection.",
            evidence=[
                experiment_path(E6, "defense_events.jsonl"),
                experiment_path(E7, "defense_events.jsonl"),
            ],
            observed=(
                f"e6_core_defense_events={core_action_count(e6_defenses)}; "
                f"e7_core_defense_events={core_action_count(e7_defenses)}; "
                f"e7_actions={format_counts(e7_actions)}"
            ),
            ok=CORE_ACTIONS.issubset(e7_core_actions)
            and core_action_count(e7_defenses) >= core_action_count(e6_defenses),
            interpretation=(
                "E7 adds ML alerting without dropping the core response vocabulary: PACE, "
                "priority reroute, stale badge, and video throttle remain present."
            ),
        ),
        row(
            check_id="RDT06",
            area="Bounded impact tradeoff",
            requirement="Reactive defense may cost mission-impact containment versus always-on rule defense, but the cost must stay bounded.",
            evidence=["outputs/batch/repeated_experiment_summary.csv"],
            observed=(
                f"e6_mission_impact_mean={fmt(e6_impact)}; "
                f"e7_mission_impact_mean={fmt(e7_impact)}; "
                f"e7_minus_e6={fmt(impact_delta)}; "
                f"e6_std={fmt(e6_std)}; e7_std={fmt(e7_std)}"
            ),
            ok=0.0 < impact_delta <= 0.03 and e7_std <= e6_std,
            interpretation=(
                "E7 is not sold as lower-impact than E6. Its observed cost is bounded while "
                "remaining stable across repeated seeds."
            ),
        ),
        row(
            check_id="RDT07",
            area="Detector threshold evidence",
            requirement="E7 traces must show both below-threshold no-op behavior and above-threshold reactive windows.",
            evidence=[experiment_path(E7, "tsra_r_decision_traces.jsonl")],
            observed=(
                f"trace_count={int(e7_trace_stats['trace_count'])}; "
                f"probability_count={int(e7_trace_stats['probability_count'])}; "
                f"threshold={fmt(e7_trace_stats['threshold'])}; "
                f"below_threshold={int(e7_trace_stats['below_threshold'])}; "
                f"above_threshold={int(e7_trace_stats['above_threshold'])}; "
                f"opened_window={int(e7_trace_stats['opened_window'])}; "
                f"no_op={int(e7_trace_stats['no_op'])}; "
                f"min_probability={fmt(e7_trace_stats['min_probability'])}; "
                f"max_probability={fmt(e7_trace_stats['max_probability'])}"
            ),
            ok=e7_trace_stats["trace_count"] == e7_trace_stats["probability_count"] == 61.0
            and e7_trace_stats["below_threshold"] > 0
            and e7_trace_stats["above_threshold"] > 0
            and e7_trace_stats["opened_window"] > 0
            and e7_trace_stats["no_op"] > 0,
            interpretation=(
                "The ML defender is not always-on: traces include no-op decisions below threshold "
                "and defense-window openings above threshold."
            ),
        ),
    ]


def format_counts(counts: Counter[str]) -> str:
    return ",".join(f"{key}:{counts[key]}" for key in sorted(counts) if key)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Reactive Defense Tradeoff Audit",
        "",
        "This audit explains what E7 gains and pays for by using ML-triggered reactive defense instead of E6 always-on rule defense.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| check_id | area | status | observed | interpretation |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(item["check_id"]),
                    md(item["area"]),
                    md(item["status"]),
                    md(item["observed"]),
                    md(item["interpretation"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Detail", ""])
    for item in rows:
        lines.extend(
            [
                f"### {item['check_id']} {item['area']}",
                "",
                f"- Requirement: {item['requirement']}",
                f"- Evidence: {item['evidence']}",
                f"- Observed: {item['observed']}",
                f"- Status: {item['status']}",
                f"- Interpretation: {item['interpretation']}",
                f"- Safety boundary: {item['safety_boundary']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit E6/E7 reactive-defense tradeoffs.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any reactive-defense tradeoff row fails.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    args = parse_args()
    rows = build_rows()
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    failed = [item for item in rows if item["status"] != "pass"]
    print(f"Wrote {display_path(args.output_csv)} ({len(rows)} rows)")
    print(f"Wrote {display_path(args.output_md)} ({len(rows)} rows)")
    if failed:
        print(f"Failed reactive-defense tradeoff rows: {', '.join(item['check_id'] for item in failed)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
