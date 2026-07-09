from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joblib import dump
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, f1_score, log_loss, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.tsra_agent.ml_policy import DEFAULT_SKLEARN_MODEL_PATH, generate_training_samples


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the TSRA-ML scikit-learn ensemble policy.")
    parser.add_argument("--samples", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=20260709)
    parser.add_argument("--output", default=str(DEFAULT_SKLEARN_MODEL_PATH))
    parser.add_argument("--report", default="models/tsra_sklearn_training_report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
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

    model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "vote",
                VotingClassifier(
                    estimators=[
                        (
                            "gb",
                            GradientBoostingClassifier(
                                n_estimators=180,
                                learning_rate=0.055,
                                max_depth=3,
                                random_state=args.seed,
                            ),
                        ),
                        (
                            "rf",
                            RandomForestClassifier(
                                n_estimators=220,
                                max_depth=9,
                                min_samples_leaf=3,
                                random_state=args.seed,
                                n_jobs=-1,
                            ),
                        ),
                    ],
                    voting="soft",
                    weights=[0.58, 0.42],
                ),
            ),
        ]
    )
    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_valid)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    metrics = {
        "validation_accuracy": round(float(accuracy_score(y_valid, predictions)), 4),
        "validation_precision": round(float(precision_score(y_valid, predictions, zero_division=0)), 4),
        "validation_recall": round(float(recall_score(y_valid, predictions, zero_division=0)), 4),
        "validation_f1": round(float(f1_score(y_valid, predictions, zero_division=0)), 4),
        "validation_roc_auc": round(float(roc_auc_score(y_valid, probabilities)), 4),
        "validation_log_loss": round(float(log_loss(y_valid, probabilities)), 4),
        "samples": float(args.samples),
        "model_family": "StandardScaler + soft-voting GradientBoosting/RandomForest",
    }

    output_path = Path(args.output)
    report_path = Path(args.report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, output_path)
    report_path.write_text(
        json.dumps(
            {
                "model_path": str(output_path),
                "report_path": str(report_path),
                "seed": args.seed,
                "samples": args.samples,
                "metrics": metrics,
                "safety_boundary": {
                    "synthetic_training_data_only": True,
                    "exploit_code": False,
                    "operational_rf_parameters": False,
                },
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"model: {output_path}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
