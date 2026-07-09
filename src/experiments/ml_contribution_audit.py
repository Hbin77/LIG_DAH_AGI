from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/ml_contribution_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/ml_contribution_audit.md"

SAFETY_BOUNDARY = (
    "closed simulation ML contribution audit only; no RF, exploit, or live network action"
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


def read_json(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(rel: str) -> list[dict[str, str]]:
    path = ROOT / rel
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


def metric(data: dict[str, Any], model_name: str, key: str) -> float:
    try:
        return float(data["models"][model_name][key])
    except (KeyError, TypeError, ValueError):
        return 0.0


def fmt(value: float) -> str:
    return f"{value:.6g}"


def int_from_row(row_data: dict[str, str], key: str) -> int:
    try:
        return int(float(row_data.get(key, "0")))
    except ValueError:
        return 0


def tool_rows(agent: str, tool_name: str) -> list[dict[str, str]]:
    return [
        item
        for item in read_csv("outputs/report_tables/agent_tool_usage_audit.csv")
        if item.get("agent") == agent and item.get("tool_name") == tool_name
    ]


def build_rows() -> list[dict[str, str]]:
    aura_metrics = read_json("outputs/models/aura_impact_model_metrics.json")
    tsra_metrics = read_json("outputs/models/tsra_detector_metrics.json")
    mps_metrics = read_json("outputs/models/aura_mps_mlp_metrics.json")

    aura_best = str(aura_metrics.get("best_model", ""))
    aura_mae = metric(aura_metrics, aura_best, "mae")
    aura_r2 = metric(aura_metrics, aura_best, "r2")
    aura_top1 = metric(aura_metrics, aura_best, "top1_action_match_rate")

    tsra_best = str(tsra_metrics.get("best_model", ""))
    tsra_precision = metric(tsra_metrics, tsra_best, "precision")
    tsra_recall = metric(tsra_metrics, tsra_best, "recall")
    tsra_f1 = metric(tsra_metrics, tsra_best, "f1")

    aura_tool_rows = tool_rows("AURA-ML", "predict_candidate_impact")
    aura_tool_invocations = sum(int_from_row(item, "invocation_count") for item in aura_tool_rows)
    aura_tool_errors = sum(int_from_row(item, "error_count") for item in aura_tool_rows)
    aura_tool_experiments = sorted({item.get("experiment", "") for item in aura_tool_rows})

    tsra_tool_rows = tool_rows("TSRA-R-ML", "predict_attack_probability")
    tsra_tool_invocations = sum(int_from_row(item, "invocation_count") for item in tsra_tool_rows)
    tsra_tool_errors = sum(int_from_row(item, "error_count") for item in tsra_tool_rows)
    tsra_tool_experiments = sorted({item.get("experiment", "") for item in tsra_tool_rows})

    metric_gate_rows = read_csv("outputs/report_tables/metric_gate_summary.csv")
    g10_rows = [item for item in metric_gate_rows if item.get("gate_id") == "G10"]
    g10 = g10_rows[0] if g10_rows else {}
    try:
        e6_e7_gap = float(g10.get("observed", "0"))
    except ValueError:
        e6_e7_gap = 0.0

    repeated_rows = {
        item.get("experiment", ""): item
        for item in read_csv("outputs/batch/repeated_experiment_summary.csv")
    }
    e6_impact = repeated_rows.get("E6_ml_aura_tsra_r", {}).get("mission_impact_mean", "")
    e7_impact = repeated_rows.get("E7_ml_aura_ml_tsra_r", {}).get("mission_impact_mean", "")

    attack_events = read_jsonl("outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl")
    defense_events = read_jsonl("outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl")
    attack_types = sorted(
        {
            str((event.get("candidate") or {}).get("attack_type", ""))
            for event in attack_events
            if event.get("candidate")
        }
    )
    defense_actions = sorted({str(event.get("action", "")) for event in defense_events})
    ml_alert_count = sum(1 for event in defense_events if event.get("action") == "ml_attack_alert")

    mps_device = str(mps_metrics.get("device", ""))
    mps_train_samples = int(mps_metrics.get("train_samples_per_epoch", 0) or 0)
    mps_epochs = int(mps_metrics.get("epochs", 0) or 0)
    mps_sample_passes = mps_train_samples * mps_epochs
    mps_top1 = float(mps_metrics.get("top1_action_match_rate", 0.0) or 0.0)
    mps_r2 = float(mps_metrics.get("r2", 0.0) or 0.0)

    return [
        row(
            check_id="M01",
            area="AURA-ML model quality",
            requirement="Deployed AURA impact predictor must be accurate enough to rank simulated attack-effect candidates.",
            evidence=["outputs/models/aura_impact_model_metrics.json"],
            observed=(
                f"best_model={aura_best}; mae={fmt(aura_mae)}; "
                f"r2={fmt(aura_r2)}; top1_action_match_rate={fmt(aura_top1)}"
            ),
            ok=aura_best == "hist_gradient_boosting"
            and aura_mae <= 0.02
            and aura_r2 >= 0.95
            and aura_top1 >= 0.85,
            interpretation=(
                "AURA-ML can use the tabular impact model for candidate ranking because both "
                "regression error and top-1 action agreement pass the closed-simulation threshold."
            ),
        ),
        row(
            check_id="M02",
            area="TSRA-R-ML detector quality",
            requirement="Deployed TSRA-R detector must have high precision, recall, and F1 before it opens defense windows.",
            evidence=["outputs/models/tsra_detector_metrics.json"],
            observed=(
                f"best_model={tsra_best}; precision={fmt(tsra_precision)}; "
                f"recall={fmt(tsra_recall)}; f1={fmt(tsra_f1)}"
            ),
            ok=tsra_best == "random_forest"
            and tsra_precision >= 0.90
            and tsra_recall >= 0.90
            and tsra_f1 >= 0.90,
            interpretation=(
                "TSRA-R-ML has enough detector quality to justify thresholded reactive defense "
                "inside the simulator."
            ),
        ),
        row(
            check_id="M03",
            area="AURA-ML tool invocation",
            requirement="AURA-ML must call the ML impact prediction tool inside DecisionTrace records.",
            evidence=["outputs/report_tables/agent_tool_usage_audit.csv"],
            observed=(
                f"experiments={','.join(aura_tool_experiments)}; "
                f"predict_candidate_impact_invocations={aura_tool_invocations}; "
                f"errors={aura_tool_errors}"
            ),
            ok=aura_tool_invocations > 0 and aura_tool_errors == 0,
            interpretation=(
                "The ML impact model is part of the AURA-ML agent loop, not only an offline metric file."
            ),
        ),
        row(
            check_id="M04",
            area="TSRA-R-ML tool invocation",
            requirement="TSRA-R-ML must call the ML anomaly-probability tool inside DecisionTrace records.",
            evidence=["outputs/report_tables/agent_tool_usage_audit.csv"],
            observed=(
                f"experiments={','.join(tsra_tool_experiments)}; "
                f"predict_attack_probability_invocations={tsra_tool_invocations}; "
                f"errors={tsra_tool_errors}"
            ),
            ok=tsra_tool_invocations > 0 and tsra_tool_errors == 0,
            interpretation=(
                "The ML detector participates in TSRA-R-ML decisions before defense events are selected."
            ),
        ),
        row(
            check_id="M05",
            area="Closed-loop ML separation",
            requirement="E7 must remain behaviorally distinct from E6 so ML TSRA-R is not a no-op copy.",
            evidence=[
                "outputs/report_tables/metric_gate_summary.csv",
                "outputs/batch/repeated_experiment_summary.csv",
            ],
            observed=(
                f"g10_status={g10.get('status', '')}; "
                f"abs_e7_minus_e6={fmt(e6_e7_gap)}; "
                f"e6_mission_impact_mean={e6_impact}; e7_mission_impact_mean={e7_impact}"
            ),
            ok=g10.get("status") == "pass" and e6_e7_gap >= 0.005,
            interpretation=(
                "The ML defender path changes closed-loop behavior relative to rule TSRA-R, "
                "so E7 is not a duplicate experiment row."
            ),
        ),
        row(
            check_id="M06",
            area="E7 ML closed-loop actions",
            requirement="E7 must include ML-selected attack diversity and ML-triggered defense actions.",
            evidence=[
                "outputs/experiments/E7_ml_aura_ml_tsra_r/attack_events.jsonl",
                "outputs/experiments/E7_ml_aura_ml_tsra_r/defense_events.jsonl",
            ],
            observed=(
                f"attack_events={len(attack_events)}; attack_types={','.join(attack_types)}; "
                f"defense_events={len(defense_events)}; ml_attack_alert_count={ml_alert_count}; "
                f"defense_actions={','.join(defense_actions)}"
            ),
            ok=len(attack_events) >= 5
            and {"queue_pressure", "failover_chasing"}.issubset(set(attack_types))
            and ml_alert_count > 0,
            interpretation=(
                "The ML-vs-ML episode contains actual ML-ranked attack choices and ML anomaly alerts."
            ),
        ),
        row(
            check_id="M07",
            area="Mac MPS scale experiment",
            requirement="GPU-scale metrics must be framed as sample-pass scale evidence, not as the deployed top-1 selector.",
            evidence=["outputs/models/aura_mps_mlp_metrics.json"],
            observed=(
                f"device={mps_device}; train_samples_per_epoch={mps_train_samples}; "
                f"epochs={mps_epochs}; sample_passes={mps_sample_passes}; "
                f"mps_r2={fmt(mps_r2)}; mps_top1_action_match_rate={fmt(mps_top1)}; "
                f"histgb_top1_action_match_rate={fmt(aura_top1)}"
            ),
            ok=mps_device == "mps" and mps_train_samples >= 1_000_000 and mps_epochs >= 20,
            interpretation=(
                "The Mac GPU run demonstrates larger synthetic sample-pass throughput. The deployed "
                "closed-loop AURA selector remains the stronger top-1 tabular model unless future "
                "MPS top-1 evidence exceeds it."
            ),
        ),
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
        "# ML Contribution Audit",
        "",
        "This audit verifies that ML contributes to bounded agent decisions inside the closed simulator.",
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
    parser = argparse.ArgumentParser(description="Audit ML contribution to agent decisions.")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any ML contribution row fails.",
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
        print(f"Failed ML contribution rows: {', '.join(item['check_id'] for item in failed)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
