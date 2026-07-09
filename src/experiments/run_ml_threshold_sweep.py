from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

from src.aura.ml_impact_predictor import MLAURA
from src.experiments.run_all import run_experiment
from src.tsra_r.ml_defender import MLTSRAR


DEFAULT_THRESHOLDS = [0.55, 0.65, 0.75, 0.85, 0.95]
DEFAULT_RUNS = 10
DEFAULT_START_SEED = 4100
DEFAULT_TMP_ROOT = Path("outputs/tmp/ml_threshold_sweep")
RAW_PATH = Path("outputs/batch/ml_threshold_sweep_raw.csv")
SUMMARY_PATH = Path("outputs/batch/ml_threshold_sweep_summary.csv")
REPORT_CSV_PATH = Path("outputs/report_tables/ml_threshold_sweep.csv")
REPORT_MD_PATH = Path("outputs/report_tables/ml_threshold_sweep.md")

CORE_ACTIONS = {"pace_switch", "priority_reroute", "stale_badge", "video_throttle"}
SAFETY_BOUNDARY = (
    "closed simulation ML threshold sweep only; no RF, exploit, or live network action"
)

RAW_FIELDNAMES = [
    "threshold",
    "seed",
    "experiment",
    "mission_impact",
    "p95_critical_latency_sec",
    "trusted_stale_exposure",
    "priority_inversion_rate",
    "kill_chain_delay_sec",
    "defense_count",
    "attack_count",
    "ml_alert_count",
    "core_defense_count",
    "pre_first_defense_events",
    "first_ml_alert_latency_sec",
    "alert_active_overlap_rate",
    "opened_window_count",
    "no_op_count",
    "below_threshold_count",
    "above_threshold_count",
    "avg_trace_probability",
    "max_trace_probability",
    "safety_boundary",
]

SUMMARY_FIELDNAMES = [
    "threshold",
    "runs",
    "mission_impact_mean",
    "mission_impact_std",
    "p95_critical_latency_sec_mean",
    "trusted_stale_exposure_mean",
    "priority_inversion_rate_mean",
    "defense_count_mean",
    "ml_alert_count_mean",
    "core_defense_count_mean",
    "pre_first_defense_events_mean",
    "first_ml_alert_latency_sec_mean",
    "alert_active_overlap_rate_mean",
    "opened_window_count_mean",
    "no_op_count_mean",
    "below_threshold_count_mean",
    "above_threshold_count_mean",
    "avg_trace_probability_mean",
    "max_trace_probability_mean",
    "tuning_status",
    "interpretation",
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


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value: float) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.6g}"


def threshold_label(threshold: float) -> str:
    return f"{threshold:.2f}"


def run_sweep(
    thresholds: list[float],
    runs: int,
    start_seed: int,
    tmp_root: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    aura_model_path = Path("outputs/models/aura_impact_model.pkl")
    detector_path = Path("outputs/models/tsra_detector.pkl")
    if not aura_model_path.exists():
        raise FileNotFoundError(f"missing AURA model: {aura_model_path}")
    if not detector_path.exists():
        raise FileNotFoundError(f"missing TSRA-R detector: {detector_path}")

    rows: list[dict[str, str]] = []
    for threshold in thresholds:
        label = threshold_label(threshold)
        for offset in range(runs):
            seed = start_seed + offset
            experiment = f"ML_threshold_{label}_seed_{seed}"
            run_experiment(
                experiment,
                seed,
                aura=MLAURA(model_path=aura_model_path),
                defender=MLTSRAR(model_path=detector_path, threshold=threshold),
                fixed_attacks=None,
                output_root=tmp_root,
            )
            exp_dir = tmp_root / experiment
            summary_rows = read_summary(exp_dir / "summary.csv")
            if not summary_rows:
                raise RuntimeError(f"missing summary row for {experiment}")
            profile = profile_run(exp_dir)
            rows.append(
                raw_row(
                    threshold=label,
                    seed=seed,
                    experiment=experiment,
                    summary=summary_rows[0],
                    profile=profile,
                )
            )
    summary = summarize_rows(rows)
    return rows, summary


def read_summary(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def profile_run(exp_dir: Path) -> dict[str, float]:
    attacks = read_jsonl(exp_dir / "attack_events.jsonl")
    defenses = read_jsonl(exp_dir / "defense_events.jsonl")
    traces = read_jsonl(exp_dir / "tsra_r_decision_traces.jsonl")

    first_attack = min(
        (as_float(attack.get("selected_at")) for attack in attacks),
        default=0.0,
    )
    ml_alerts = [defense for defense in defenses if defense.get("action") == "ml_attack_alert"]
    core_count = sum(1 for defense in defenses if defense.get("action") in CORE_ACTIONS)
    pre_first = sum(1 for defense in defenses if as_float(defense.get("time_sec")) < first_attack)
    first_alert_latency = min(
        (
            as_float(alert.get("time_sec")) - first_attack
            for alert in ml_alerts
            if as_float(alert.get("time_sec")) >= first_attack
        ),
        default=math.nan,
    )
    alert_overlap_rate = active_attack_overlap_rate(ml_alerts, attacks)

    probabilities = []
    threshold = 0.0
    opened = 0
    no_op = 0
    for trace in traces:
        feedback = trace.get("feedback") or {}
        if "probability" in feedback:
            probabilities.append(as_float(feedback.get("probability")))
        if "threshold" in feedback:
            threshold = max(threshold, as_float(feedback.get("threshold")))
        if feedback.get("opened_window"):
            opened += 1
        selected = trace.get("selected_action") or {}
        if selected.get("type") == "no_op":
            no_op += 1
    below = sum(1 for probability in probabilities if probability < threshold)
    above = sum(1 for probability in probabilities if probability >= threshold)

    return {
        "ml_alert_count": float(len(ml_alerts)),
        "core_defense_count": float(core_count),
        "pre_first_defense_events": float(pre_first),
        "first_ml_alert_latency_sec": first_alert_latency,
        "alert_active_overlap_rate": alert_overlap_rate,
        "opened_window_count": float(opened),
        "no_op_count": float(no_op),
        "below_threshold_count": float(below),
        "above_threshold_count": float(above),
        "avg_trace_probability": (
            sum(probabilities) / len(probabilities) if probabilities else math.nan
        ),
        "max_trace_probability": max(probabilities) if probabilities else math.nan,
    }


def active_attack_overlap_rate(
    alerts: list[dict[str, Any]],
    attacks: list[dict[str, Any]],
) -> float:
    if not alerts:
        return 0.0
    windows = []
    for attack in attacks:
        candidate = attack.get("candidate") or {}
        start = as_float(attack.get("selected_at"))
        end = start + as_float(candidate.get("duration_sec"))
        windows.append((start, end))
    overlap = 0
    for alert in alerts:
        t = as_float(alert.get("time_sec"))
        if any(start <= t <= end for start, end in windows):
            overlap += 1
    return overlap / len(alerts)


def raw_row(
    *,
    threshold: str,
    seed: int,
    experiment: str,
    summary: dict[str, str],
    profile: dict[str, float],
) -> dict[str, str]:
    row = {
        "threshold": threshold,
        "seed": str(seed),
        "experiment": experiment,
        "mission_impact": summary.get("mission_impact", ""),
        "p95_critical_latency_sec": summary.get("p95_critical_latency_sec", ""),
        "trusted_stale_exposure": summary.get("trusted_stale_exposure", ""),
        "priority_inversion_rate": summary.get("priority_inversion_rate", ""),
        "kill_chain_delay_sec": summary.get("kill_chain_delay_sec", ""),
        "defense_count": summary.get("defense_count", ""),
        "attack_count": summary.get("attack_count", ""),
        "safety_boundary": SAFETY_BOUNDARY,
    }
    for key, value in profile.items():
        row[key] = fmt(value)
    return row


def summarize_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault(row["threshold"], []).append(row)

    summary_rows = []
    for threshold in sorted(groups, key=lambda item: float(item)):
        group = groups[threshold]
        metrics = {
            "mission_impact": mean_std(group, "mission_impact"),
            "p95_critical_latency_sec": mean_std(group, "p95_critical_latency_sec"),
            "trusted_stale_exposure": mean_std(group, "trusted_stale_exposure"),
            "priority_inversion_rate": mean_std(group, "priority_inversion_rate"),
            "defense_count": mean_std(group, "defense_count"),
            "ml_alert_count": mean_std(group, "ml_alert_count"),
            "core_defense_count": mean_std(group, "core_defense_count"),
            "pre_first_defense_events": mean_std(group, "pre_first_defense_events"),
            "first_ml_alert_latency_sec": mean_std(group, "first_ml_alert_latency_sec"),
            "alert_active_overlap_rate": mean_std(group, "alert_active_overlap_rate"),
            "opened_window_count": mean_std(group, "opened_window_count"),
            "no_op_count": mean_std(group, "no_op_count"),
            "below_threshold_count": mean_std(group, "below_threshold_count"),
            "above_threshold_count": mean_std(group, "above_threshold_count"),
            "avg_trace_probability": mean_std(group, "avg_trace_probability"),
            "max_trace_probability": mean_std(group, "max_trace_probability"),
        }
        status = tuning_status(metrics)
        summary_rows.append(
            {
                "threshold": threshold,
                "runs": str(len(group)),
                "mission_impact_mean": fmt(metrics["mission_impact"][0]),
                "mission_impact_std": fmt(metrics["mission_impact"][1]),
                "p95_critical_latency_sec_mean": fmt(metrics["p95_critical_latency_sec"][0]),
                "trusted_stale_exposure_mean": fmt(metrics["trusted_stale_exposure"][0]),
                "priority_inversion_rate_mean": fmt(metrics["priority_inversion_rate"][0]),
                "defense_count_mean": fmt(metrics["defense_count"][0]),
                "ml_alert_count_mean": fmt(metrics["ml_alert_count"][0]),
                "core_defense_count_mean": fmt(metrics["core_defense_count"][0]),
                "pre_first_defense_events_mean": fmt(metrics["pre_first_defense_events"][0]),
                "first_ml_alert_latency_sec_mean": fmt(metrics["first_ml_alert_latency_sec"][0]),
                "alert_active_overlap_rate_mean": fmt(metrics["alert_active_overlap_rate"][0]),
                "opened_window_count_mean": fmt(metrics["opened_window_count"][0]),
                "no_op_count_mean": fmt(metrics["no_op_count"][0]),
                "below_threshold_count_mean": fmt(metrics["below_threshold_count"][0]),
                "above_threshold_count_mean": fmt(metrics["above_threshold_count"][0]),
                "avg_trace_probability_mean": fmt(metrics["avg_trace_probability"][0]),
                "max_trace_probability_mean": fmt(metrics["max_trace_probability"][0]),
                "tuning_status": status,
                "interpretation": interpret_threshold(float(threshold), metrics, status),
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return summary_rows


def mean_std(rows: list[dict[str, str]], key: str) -> tuple[float, float]:
    values = []
    for row in rows:
        value = as_float(row.get(key), default=math.nan)
        if not math.isnan(value):
            values.append(value)
    if not values:
        return math.nan, math.nan
    if len(values) == 1:
        return values[0], 0.0
    return statistics.fmean(values), statistics.stdev(values)


def tuning_status(metrics: dict[str, tuple[float, float]]) -> str:
    mission_impact = metrics["mission_impact"][0]
    overlap = metrics["alert_active_overlap_rate"][0]
    pre_first = metrics["pre_first_defense_events"][0]
    core_count = metrics["core_defense_count"][0]
    latency = metrics["first_ml_alert_latency_sec"][0]
    if (
        mission_impact <= 0.20
        and overlap >= 0.80
        and pre_first <= 0.20
        and core_count >= 10.0
        and latency <= 80.0
    ):
        return "usable"
    return "watch"


def interpret_threshold(
    threshold: float,
    metrics: dict[str, tuple[float, float]],
    status: str,
) -> str:
    impact = metrics["mission_impact"][0]
    alerts = metrics["ml_alert_count"][0]
    latency = metrics["first_ml_alert_latency_sec"][0]
    no_op = metrics["no_op_count"][0]
    if threshold < 0.70:
        band = "lower threshold opens reactive windows more readily"
    elif threshold <= 0.80:
        band = "baseline threshold balances alert timing and no-op evidence"
    else:
        band = "higher threshold requires stronger anomaly probability before action"
    return (
        f"{band}; status={status}; impact_mean={impact:.3f}; "
        f"alert_mean={alerts:.2f}; first_alert_latency_mean={latency:.1f}s; no_op_mean={no_op:.1f}"
    )


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ML Threshold Sweep",
        "",
        "This table sweeps the TSRA-R-ML anomaly threshold across closed simulation runs.",
        "The sweep does not change the deployed E7 baseline by itself; it records the tuning tradeoff around the baseline threshold.",
        f"Safety boundary: {SAFETY_BOUNDARY}",
        "",
        "| threshold | runs | mission impact mean | ML alerts mean | first alert latency mean | no-op mean | status | interpretation |",
        "|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["threshold"]),
                    md(row["runs"]),
                    md(row["mission_impact_mean"]),
                    md(row["ml_alert_count_mean"]),
                    md(row["first_ml_alert_latency_sec_mean"]),
                    md(row["no_op_count_mean"]),
                    md(row["tuning_status"]),
                    md(row["interpretation"]),
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def md(value: str) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ML TSRA-R threshold sweep.")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--start-seed", type=int, default=DEFAULT_START_SEED)
    parser.add_argument("--tmp-root", type=Path, default=DEFAULT_TMP_ROOT)
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=DEFAULT_THRESHOLDS,
        help="Threshold values to sweep.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows, summary_rows = run_sweep(
        thresholds=args.thresholds,
        runs=args.runs,
        start_seed=args.start_seed,
        tmp_root=args.tmp_root,
    )
    write_csv(RAW_PATH, rows, RAW_FIELDNAMES)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_FIELDNAMES)
    write_csv(REPORT_CSV_PATH, summary_rows, SUMMARY_FIELDNAMES)
    write_report(REPORT_MD_PATH, summary_rows)
    print(f"Wrote {RAW_PATH} ({len(rows)} rows)")
    print(f"Wrote {SUMMARY_PATH} ({len(summary_rows)} rows)")
    print(f"Wrote {REPORT_CSV_PATH} ({len(summary_rows)} rows)")
    print(f"Wrote {REPORT_MD_PATH} ({len(summary_rows)} rows)")
    print(
        "Threshold sweep: "
        + ", ".join(
            f"{row['threshold']} impact={row['mission_impact_mean']} status={row['tuning_status']}"
            for row in summary_rows
        )
    )


if __name__ == "__main__":
    main()
