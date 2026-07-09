from __future__ import annotations

import argparse
import csv
import math
import pickle
from pathlib import Path
from typing import Any

from src.ml.train_tsra_detector import build_detector_rows


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_CSV = ROOT / "outputs/report_tables/tsra_detector_calibration_audit.csv"
DEFAULT_OUTPUT_MD = ROOT / "outputs/report_tables/tsra_detector_calibration_audit.md"
DEFAULT_BINS_CSV = ROOT / "outputs/report_tables/tsra_detector_calibration_bins.csv"
DEFAULT_MODEL_PATH = ROOT / "outputs/models/tsra_detector.pkl"

DEFAULT_ROWS = 4000
DEFAULT_SEED = 9100
THRESHOLDS = [0.55, 0.65, 0.75, 0.85, 0.95]
SAFETY_BOUNDARY = (
    "closed simulation TSRA-R detector calibration audit only; no RF, exploit, or live network action"
)

AUDIT_FIELDNAMES = [
    "check_id",
    "area",
    "requirement",
    "evidence",
    "observed",
    "status",
    "interpretation",
    "safety_boundary",
]

BINS_FIELDNAMES = [
    "bin_id",
    "probability_min",
    "probability_max",
    "sample_count",
    "avg_probability",
    "observed_attack_rate",
    "absolute_gap",
    "safety_boundary",
]


def load_model(path: Path) -> Any:
    with path.open("rb") as f:
        return pickle.load(f)


def build_holdout(rows: int, seed: int) -> tuple[list[dict[str, Any]], list[int]]:
    records = build_detector_rows(rows, seed)
    features = []
    labels = []
    for record in records:
        labels.append(int(record["attack_present"]))
        feature = dict(record)
        for key in ["attack_present", "attack_type", "sample_id"]:
            feature.pop(key, None)
        features.append(feature)
    return features, labels


def brier_score(probabilities: list[float], labels: list[int]) -> float:
    return sum((probability - label) ** 2 for probability, label in zip(probabilities, labels)) / len(labels)


def calibration_bins(
    probabilities: list[float],
    labels: list[int],
    bin_count: int = 10,
) -> list[dict[str, str]]:
    rows = []
    for index in range(bin_count):
        lower = index / bin_count
        upper = (index + 1) / bin_count
        selected = [
            row_index
            for row_index, probability in enumerate(probabilities)
            if (lower <= probability < upper if index < bin_count - 1 else lower <= probability <= upper)
        ]
        if selected:
            avg_probability = sum(probabilities[row_index] for row_index in selected) / len(selected)
            observed_rate = sum(labels[row_index] for row_index in selected) / len(selected)
            absolute_gap = abs(avg_probability - observed_rate)
        else:
            avg_probability = math.nan
            observed_rate = math.nan
            absolute_gap = math.nan
        rows.append(
            {
                "bin_id": f"B{index + 1:02d}",
                "probability_min": fmt(lower),
                "probability_max": fmt(upper),
                "sample_count": str(len(selected)),
                "avg_probability": fmt(avg_probability),
                "observed_attack_rate": fmt(observed_rate),
                "absolute_gap": fmt(absolute_gap),
                "safety_boundary": SAFETY_BOUNDARY,
            }
        )
    return rows


def expected_calibration_error(bin_rows: list[dict[str, str]], total_count: int) -> float:
    ece = 0.0
    for row in bin_rows:
        count = int(row["sample_count"])
        gap = as_float(row["absolute_gap"], default=0.0)
        ece += (count / total_count) * gap
    return ece


def threshold_metrics(probabilities: list[float], labels: list[int], threshold: float) -> dict[str, float]:
    tp = fp = fn = tn = 0
    for probability, label in zip(probabilities, labels):
        predicted = probability >= threshold
        if predicted and label:
            tp += 1
        elif predicted and not label:
            fp += 1
        elif not predicted and label:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    fnr = fn / (fn + tp) if fn + tp else 0.0
    return {
        "tp": float(tp),
        "fp": float(fp),
        "fn": float(fn),
        "tn": float(tn),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
    }


def quantile(values: list[float], fraction: float) -> float:
    if not values:
        return math.nan
    sorted_values = sorted(values)
    index = int((len(sorted_values) - 1) * fraction)
    return sorted_values[index]


def fmt(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if math.isnan(number):
        return ""
    return f"{number:.6g}"


def as_float(value: Any, default: float = math.nan) -> float:
    try:
        if value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_audit_rows(
    *,
    model_path: Path,
    holdout_rows: int,
    seed: int,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    model = load_model(model_path)
    features, labels = build_holdout(holdout_rows, seed)
    probabilities = [float(item[1]) for item in model.predict_proba(features)]
    bins = calibration_bins(probabilities, labels)
    brier = brier_score(probabilities, labels)
    ece = expected_calibration_error(bins, len(labels))
    prevalence = sum(labels) / len(labels)
    threshold_results = {
        threshold: threshold_metrics(probabilities, labels, threshold)
        for threshold in THRESHOLDS
    }

    positives = [probability for probability, label in zip(probabilities, labels) if label]
    negatives = [probability for probability, label in zip(probabilities, labels) if not label]
    positive_median = quantile(positives, 0.50)
    positive_q75 = quantile(positives, 0.75)
    negative_median = quantile(negatives, 0.50)
    negative_q95 = quantile(negatives, 0.95)

    sweep_rows = read_csv(ROOT / "outputs/batch/ml_threshold_sweep_summary.csv")
    sweep_by_threshold = {item["threshold"]: item for item in sweep_rows}
    baseline_sweep = sweep_by_threshold.get("0.75", {})
    high_sweep = sweep_by_threshold.get("0.95", {})

    baseline = threshold_results[0.75]
    low = threshold_results[0.55]
    high = threshold_results[0.95]

    audit_rows = [
        row(
            check_id="CAL01",
            area="Holdout coverage",
            requirement="Calibration audit must use an independent deterministic holdout set.",
            evidence=["src/ml/train_tsra_detector.py", "outputs/models/tsra_detector.pkl"],
            observed=(
                f"holdout_rows={len(labels)}; seed={seed}; prevalence={fmt(prevalence)}; "
                f"probability_min={fmt(min(probabilities))}; probability_max={fmt(max(probabilities))}; "
                f"probability_mean={fmt(sum(probabilities) / len(probabilities))}"
            ),
            ok=len(labels) == holdout_rows and 0.45 <= prevalence <= 0.55,
            interpretation="The calibration audit uses a balanced deterministic synthetic holdout separate from the saved metric JSON.",
        ),
        row(
            check_id="CAL02",
            area="Probability calibration",
            requirement="Detector probabilities must be usable for thresholding while exposing calibration error.",
            evidence=["outputs/report_tables/tsra_detector_calibration_bins.csv"],
            observed=f"brier_score={fmt(brier)}; expected_calibration_error={fmt(ece)}; bins={len(bins)}",
            ok=brier <= 0.05 and ece <= 0.12 and len(bins) == 10,
            interpretation=(
                "Brier score is strong and ECE is acceptable for closed-simulation thresholding; "
                "the audit still records that probabilities are not perfect calibrated truths."
            ),
        ),
        row(
            check_id="CAL03",
            area="Baseline threshold quality",
            requirement="The deployed 0.75 threshold must provide high precision and bounded false positives.",
            evidence=["outputs/report_tables/tsra_detector_calibration_audit.csv"],
            observed=(
                "threshold=0.75; "
                f"precision={fmt(baseline['precision'])}; recall={fmt(baseline['recall'])}; "
                f"f1={fmt(baseline['f1'])}; false_positive_rate={fmt(baseline['false_positive_rate'])}; "
                f"false_negative_rate={fmt(baseline['false_negative_rate'])}; "
                f"tp={int(baseline['tp'])}; fp={int(baseline['fp'])}; fn={int(baseline['fn'])}; tn={int(baseline['tn'])}"
            ),
            ok=baseline["precision"] >= 0.98
            and baseline["recall"] >= 0.80
            and baseline["false_positive_rate"] <= 0.005,
            interpretation=(
                "The 0.75 detector threshold is conservative: it sharply limits false positives "
                "while retaining enough attack recall for reactive defense."
            ),
        ),
        row(
            check_id="CAL04",
            area="Threshold sensitivity",
            requirement="Higher thresholds must show the expected precision/recall tradeoff.",
            evidence=["outputs/report_tables/tsra_detector_calibration_audit.csv"],
            observed=(
                f"threshold_0.55_precision={fmt(low['precision'])}; "
                f"threshold_0.55_recall={fmt(low['recall'])}; "
                f"threshold_0.75_precision={fmt(baseline['precision'])}; "
                f"threshold_0.75_recall={fmt(baseline['recall'])}; "
                f"threshold_0.95_precision={fmt(high['precision'])}; "
                f"threshold_0.95_recall={fmt(high['recall'])}"
            ),
            ok=high["recall"] < baseline["recall"] < low["recall"]
            and baseline["precision"] >= low["precision"]
            and high["precision"] >= baseline["precision"],
            interpretation=(
                "The detector behaves monotonically enough for threshold tuning: higher threshold "
                "reduces recall while preserving high precision."
            ),
        ),
        row(
            check_id="CAL05",
            area="Class probability separation",
            requirement="Attack and non-attack holdout states must separate in probability space.",
            evidence=["outputs/report_tables/tsra_detector_calibration_audit.csv"],
            observed=(
                f"positive_median={fmt(positive_median)}; positive_q75={fmt(positive_q75)}; "
                f"negative_median={fmt(negative_median)}; negative_q95={fmt(negative_q95)}; "
                f"median_gap={fmt(positive_median - negative_median)}"
            ),
            ok=(positive_median - negative_median) >= 0.70
            and negative_q95 < 0.75
            and positive_q75 > 0.90,
            interpretation=(
                "Attack-present states cluster near high probabilities and non-attack states stay low, "
                "which supports threshold-triggered defense windows."
            ),
        ),
        row(
            check_id="CAL06",
            area="Closed-loop threshold consistency",
            requirement="Offline detector calibration must agree with the closed-loop threshold sweep direction.",
            evidence=[
                "outputs/batch/ml_threshold_sweep_summary.csv",
                "outputs/report_tables/ml_threshold_sweep.csv",
            ],
            observed=(
                f"sweep_0.75_status={baseline_sweep.get('tuning_status', '')}; "
                f"sweep_0.75_impact={baseline_sweep.get('mission_impact_mean', '')}; "
                f"sweep_0.95_status={high_sweep.get('tuning_status', '')}; "
                f"sweep_0.95_impact={high_sweep.get('mission_impact_mean', '')}; "
                f"offline_0.75_recall={fmt(baseline['recall'])}; offline_0.95_recall={fmt(high['recall'])}"
            ),
            ok=baseline_sweep.get("tuning_status") == "usable"
            and high_sweep.get("tuning_status") == "watch"
            and as_float(high_sweep.get("mission_impact_mean"), 0.0)
            > as_float(baseline_sweep.get("mission_impact_mean"), 1.0)
            and high["recall"] < baseline["recall"],
            interpretation=(
                "Offline calibration and closed-loop sweep agree: an overly high threshold loses recall "
                "and increases mission impact."
            ),
        ),
    ]
    return audit_rows, bins


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# TSRA-R Detector Calibration Audit",
        "",
        "This audit checks whether the TSRA-R-ML detector probabilities are usable for closed-simulation thresholded defense.",
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
    parser = argparse.ArgumentParser(description="Audit TSRA-R detector probability calibration.")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--bins-csv", type=Path, default=DEFAULT_BINS_CSV)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with a non-zero status if any calibration row fails.",
    )
    return parser.parse_args()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    args = parse_args()
    rows, bins = build_audit_rows(
        model_path=args.model_path,
        holdout_rows=args.rows,
        seed=args.seed,
    )
    write_csv(args.output_csv, rows, AUDIT_FIELDNAMES)
    write_csv(args.bins_csv, bins, BINS_FIELDNAMES)
    write_markdown(args.output_md, rows)
    failed = [item for item in rows if item["status"] != "pass"]
    print(f"Wrote {display_path(args.output_csv)} ({len(rows)} rows)")
    print(f"Wrote {display_path(args.output_md)} ({len(rows)} rows)")
    print(f"Wrote {display_path(args.bins_csv)} ({len(bins)} rows)")
    if failed:
        print(f"Failed calibration rows: {', '.join(item['check_id'] for item in failed)}")
        if args.fail_on_error:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
