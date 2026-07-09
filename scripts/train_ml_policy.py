from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tsra_agent.ml_policy import (
    DEFAULT_MODEL_PATH,
    evaluate_classifier,
    generate_training_samples,
    save_model,
    split_samples,
    train_model,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the TSRA-ML risk classifier.")
    parser.add_argument("--samples", type=int, default=8000)
    parser.add_argument("--seed", type=int, default=20260709)
    parser.add_argument("--epochs", type=int, default=240)
    parser.add_argument("--output", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--report", default="models/tsra_ml_training_report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    samples = generate_training_samples(args.samples, args.seed)
    train_samples, validation_samples = split_samples(samples)
    model = train_model(train_samples, epochs=args.epochs)
    train_metrics = model.metrics
    validation_metrics = evaluate_classifier(model, validation_samples)
    model.metrics = {
        "train_accuracy": train_metrics["accuracy"],
        "train_precision": train_metrics["precision"],
        "train_recall": train_metrics["recall"],
        "train_f1": train_metrics["f1"],
        "train_log_loss": train_metrics["log_loss"],
        "validation_accuracy": validation_metrics["accuracy"],
        "validation_precision": validation_metrics["precision"],
        "validation_recall": validation_metrics["recall"],
        "validation_f1": validation_metrics["f1"],
        "validation_log_loss": validation_metrics["log_loss"],
        "samples": float(args.samples),
    }

    output_path = Path(args.output)
    report_path = Path(args.report)
    save_model(model, output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "model_path": str(output_path),
                "report_path": str(report_path),
                "seed": args.seed,
                "samples": args.samples,
                "epochs": args.epochs,
                "metrics": model.metrics,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(json.dumps(model.metrics, indent=2, ensure_ascii=False))
    print(f"model: {output_path}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
