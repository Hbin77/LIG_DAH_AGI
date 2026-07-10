from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from statistics import mean
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sklearn
import joblib
import numpy
from joblib import dump
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from src.tsra_agent.ml_policy import (
    DATASET_GENERATOR_VERSION,
    DEFAULT_SKLEARN_MODEL_PATH,
    FEATURE_NAMES,
    INTERVENTION_LATENCY_THRESHOLD,
    INTERVENTION_RISK_THRESHOLD,
    INTERVENTION_STALE_THRESHOLD,
    generate_training_samples,
    oracle_label,
    state_to_features,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train and validate the TSRA-ML risk policy.")
    parser.add_argument("--samples", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=20260709)
    parser.add_argument("--trajectory-seeds", default="41,43,47,53,59")
    parser.add_argument("--trajectory-ticks", type=int, default=180)
    parser.add_argument("--output", default=str(DEFAULT_SKLEARN_MODEL_PATH))
    parser.add_argument("--report", default="models/tsra_sklearn_training_report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.samples < 1000:
        raise ValueError("--samples must be at least 1000 for the primary model")
    trajectory_seeds = parse_seeds(args.trajectory_seeds)
    samples = generate_training_samples(args.samples, args.seed)
    x = [sample.features for sample in samples]
    y = [sample.label for sample in samples]
    x_train, x_valid, y_train, y_valid = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=args.seed,
        stratify=y,
    )

    model = HistGradientBoostingClassifier(
        max_iter=400,
        learning_rate=0.055,
        max_leaf_nodes=63,
        min_samples_leaf=12,
        l2_regularization=0.10,
        random_state=args.seed,
    )
    model.fit(x_train, y_train)
    validation_probabilities = model.predict_proba(x_valid)[:, 1]
    validation_metrics = classification_metrics(y_valid, validation_probabilities)
    metrics = {
        "validation_accuracy": validation_metrics["accuracy"],
        "validation_precision": validation_metrics["precision"],
        "validation_recall": validation_metrics["recall"],
        "validation_f1": validation_metrics["f1"],
        "validation_roc_auc": validation_metrics["roc_auc"],
        "validation_log_loss": validation_metrics["log_loss"],
        "validation_brier_score": validation_metrics["brier_score"],
        "samples": args.samples,
        "model_family": "HistGradientBoostingClassifier",
    }

    output_path = Path(args.output)
    report_path = Path(args.report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, output_path)
    model_sha256 = hashlib.sha256(output_path.read_bytes()).hexdigest()

    trajectory_validation = evaluate_closed_loop_trajectories(
        model,
        seeds=trajectory_seeds,
        ticks=args.trajectory_ticks,
    )
    profile = profile_training_data(x, y)
    report = {
        "schema_version": "tsra-sklearn-training/v2",
        "model_path": display_path(output_path),
        "model_sha256": model_sha256,
        "report_path": str(report_path),
        "seed": args.seed,
        "samples": args.samples,
        "feature_names": FEATURE_NAMES,
        "feature_count": len(FEATURE_NAMES),
        "dataset_generator_version": DATASET_GENERATOR_VERSION,
        "label_definition": (
            "Synthetic proactive-intervention oracle: weighted mission risk >= "
            f"{INTERVENTION_RISK_THRESHOLD}, critical-latency pressure >= "
            f"{INTERVENTION_LATENCY_THRESHOLD}, or stale ratio >= "
            f"{INTERVENTION_STALE_THRESHOLD}."
        ),
        "label_thresholds": {
            "weighted_mission_risk": INTERVENTION_RISK_THRESHOLD,
            "critical_latency_pressure": INTERVENTION_LATENCY_THRESHOLD,
            "stale_ratio": INTERVENTION_STALE_THRESHOLD,
        },
        "metrics": metrics,
        "validation_diagnostics": validation_metrics,
        "data_quality": profile,
        "closed_loop_oracle_validation": {
            "seeds": trajectory_seeds,
            "ticks": args.trajectory_ticks,
            "conditions": trajectory_validation,
            "interpretation": (
                "Compares model output with the same synthetic risk oracle on independent "
                "simulator trajectories; it is not real-world attack ground truth."
            ),
        },
        "runtime": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": numpy.__version__,
            "joblib": joblib.__version__,
        },
        "limitations": [
            "All labels are synthetic oracle labels, not operational SATCOM incident labels.",
            "Random holdout measures interpolation on the generated distribution.",
            "Closed-loop validation uses independent seeds but the same mission simulator.",
            "No real-world generalization or calibrated operational probability is claimed.",
        ],
        "safety_boundary": {
            "synthetic_training_data_only": True,
            "exploit_code": False,
            "operational_rf_parameters": False,
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(json.dumps(trajectory_validation, indent=2, ensure_ascii=False))
    print(f"model: {output_path}")
    print(f"report: {report_path}")


def parse_seeds(value: str) -> list[int]:
    seeds = [int(part.strip()) for part in value.split(",") if part.strip()]
    if not seeds:
        raise ValueError("trajectory seed list must contain at least one integer")
    return seeds


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def classification_metrics(labels: list[int], probabilities: Any) -> dict[str, Any]:
    predictions = [int(float(probability) >= 0.5) for probability in probabilities]
    true_positive = sum(label == prediction == 1 for label, prediction in zip(labels, predictions))
    false_positive = sum(label == 0 and prediction == 1 for label, prediction in zip(labels, predictions))
    true_negative = sum(label == prediction == 0 for label, prediction in zip(labels, predictions))
    false_negative = sum(label == 1 and prediction == 0 for label, prediction in zip(labels, predictions))
    has_both_classes = len(set(labels)) == 2
    return {
        "rows": len(labels),
        "positive_rows": sum(labels),
        "positive_rate": round(sum(labels) / max(1, len(labels)), 4),
        "predicted_positive_rows": sum(predictions),
        "accuracy": round(float(accuracy_score(labels, predictions)), 4),
        "precision": round(float(precision_score(labels, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(labels, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(labels, predictions, zero_division=0)), 4),
        "roc_auc": (
            round(float(roc_auc_score(labels, probabilities)), 4)
            if has_both_classes
            else None
        ),
        "log_loss": round(float(log_loss(labels, probabilities, labels=[0, 1])), 4),
        "brier_score": round(float(brier_score_loss(labels, probabilities)), 4),
        "false_positive_rate": round(false_positive / max(1, false_positive + true_negative), 4),
        "false_negative_rate": round(false_negative / max(1, false_negative + true_positive), 4),
        "confusion": {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
        },
    }


def profile_training_data(features: list[list[float]], labels: list[int]) -> dict[str, Any]:
    duplicate_rows = len(features) - len({tuple(row) for row in features})
    out_of_range = sum(
        value < 0.0 or value > 1.0
        for row in features
        for value in row
    )
    feature_summary = {}
    for index, name in enumerate(FEATURE_NAMES):
        values = [row[index] for row in features]
        feature_summary[name] = {
            "min": round(min(values), 6),
            "max": round(max(values), 6),
            "mean": round(mean(values), 6),
        }
    return {
        "grain": "one synthetic mission-state feature vector",
        "rows": len(features),
        "columns": len(FEATURE_NAMES),
        "missing_value_count": 0,
        "exact_duplicate_rows": duplicate_rows,
        "out_of_range_value_count": out_of_range,
        "class_counts": {
            "0": labels.count(0),
            "1": labels.count(1),
        },
        "class_balance_delta": abs(labels.count(0) - labels.count(1)),
        "feature_summary": feature_summary,
    }


def evaluate_closed_loop_trajectories(
    model: HistGradientBoostingClassifier,
    *,
    seeds: list[int],
    ticks: int,
) -> dict[str, dict[str, Any]]:
    from src.tsra_agent.models import AttackMode
    from src.tsra_agent.simulator import MissionSimulator

    conditions = {
        "baseline": lambda seed: MissionSimulator(
            ticks,
            seed,
            AttackMode.NONE,
            defense_enabled=False,
        ).run("baseline"),
        "attacked": lambda seed: MissionSimulator(
            ticks,
            seed,
            AttackMode.HYBRID,
            defense_enabled=False,
        ).run("attacked"),
        "tsra_defended": lambda seed: MissionSimulator(
            ticks,
            seed,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="tsra",
        ).run("tsra_defended"),
    }
    result = {}
    for name, run_condition in conditions.items():
        rows: list[list[float]] = []
        for seed in seeds:
            simulation = run_condition(seed)
            for trace in simulation.traces["aura"]:
                signals = SimpleNamespace(**trace["observation"]["signals"])
                rows.append(state_to_features(signals))
        labels = [oracle_label(row) for row in rows]
        probabilities = model.predict_proba(rows)[:, 1]
        result[name] = classification_metrics(labels, probabilities)
    return result


if __name__ == "__main__":
    main()
