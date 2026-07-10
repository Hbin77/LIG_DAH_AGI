from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch
import numpy
from torch import nn


FEATURE_COUNT = 28


class AuraRankingMLP(nn.Module):
    def __init__(self, input_dim: int = FEATURE_COUNT) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 192),
            nn.GELU(),
            nn.LayerNorm(192),
            nn.Dropout(0.08),
            nn.Linear(192, 192),
            nn.GELU(),
            nn.Dropout(0.08),
            nn.Linear(192, 96),
            nn.GELU(),
            nn.Linear(96, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features).squeeze(-1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train an optional AURA listwise-ranking MLP on validated rollout labels."
    )
    parser.add_argument(
        "--dataset",
        default="outputs/datasets/aura_counterfactual_rollouts.jsonl",
    )
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="mps")
    parser.add_argument("--samples-per-epoch", type=int, default=1_000_000)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-groups", type=int, default=8192)
    parser.add_argument("--learning-rate", type=float, default=8e-4)
    parser.add_argument("--rank-weight", type=float, default=0.45)
    parser.add_argument("--seed", type=int, default=20260710)
    parser.add_argument("--output", default="models/aura_mps_student.pt")
    parser.add_argument(
        "--export",
        default="models/aura_mps_student_weights.npz",
    )
    parser.add_argument("--metrics", default="models/aura_mps_student_metrics.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.samples_per_epoch < 100_000:
        raise ValueError("GPU scale run requires at least 100,000 sample-passes per epoch")
    if args.epochs < 2:
        raise ValueError("at least two epochs are required")
    device = choose_device(args.device)
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"missing {dataset_path}; run .venv/bin/python scripts/train_aura_rollout_policy.py first"
        )

    training_report = read_json(ROOT / "models" / "aura_rollout_training_report.json")
    rows = [
        json.loads(line)
        for line in dataset_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    train_rows = [row for row in rows if row["split"] == "train"]
    validation_rows = [row for row in rows if row["split"] == "validation"]
    validate_dataset(train_rows, validation_rows, training_report)
    train_groups = materialize_groups(train_rows)
    validation_groups = materialize_groups(validation_rows)

    train_x = torch.tensor(
        [[row["features"] for row in group] for group in train_groups],
        dtype=torch.float32,
        device=device,
    )
    train_y_raw = torch.tensor(
        [
            [row["label_incremental_impact"] for row in group]
            for group in train_groups
        ],
        dtype=torch.float32,
        device=device,
    )
    label_mean = float(train_y_raw.mean().item())
    label_scale = max(float(train_y_raw.std(unbiased=False).item()), 1e-6)
    train_y = (train_y_raw - label_mean) / label_scale

    torch.manual_seed(args.seed)
    model = AuraRankingMLP().to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=2e-4,
    )
    regression_loss = nn.SmoothL1Loss(beta=0.20)
    if args.samples_per_epoch % 4 != 0:
        raise ValueError("samples-per-epoch must be divisible by four candidate rows")
    groups_per_epoch = args.samples_per_epoch // 4
    steps_per_epoch = max(1, math.ceil(groups_per_epoch / args.batch_groups))
    history = []
    best_state: dict[str, torch.Tensor] | None = None
    best_metrics: dict[str, float | int] | None = None
    best_epoch = 0

    started = time.perf_counter()
    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = 0.0
        remaining_groups = groups_per_epoch
        for _ in range(steps_per_epoch):
            current_batch_groups = min(args.batch_groups, remaining_groups)
            group_indices = torch.randint(
                0,
                train_x.shape[0],
                (current_batch_groups,),
                device=device,
            )
            features = train_x[group_indices]
            labels = train_y[group_indices]
            optimizer.zero_grad(set_to_none=True)
            predictions = model(features)
            regression = regression_loss(predictions, labels)
            target_distribution = torch.softmax(labels / 0.45, dim=1)
            ranking = -(
                target_distribution
                * torch.log_softmax(predictions / 0.45, dim=1)
            ).sum(dim=1).mean()
            loss = regression + args.rank_weight * ranking
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.item())
            remaining_groups -= current_batch_groups
        if remaining_groups != 0:
            raise RuntimeError("GPU epoch sample-pass accounting mismatch")

        validation_predictions = predict_rows(
            model,
            validation_rows,
            device,
            label_mean,
            label_scale,
        )
        metrics = evaluate_predictions(validation_rows, validation_predictions)
        metrics["epoch"] = epoch
        metrics["training_loss"] = round(epoch_loss / steps_per_epoch, 6)
        history.append(metrics)
        if best_metrics is None or model_order(metrics) < model_order(best_metrics):
            best_metrics = metrics
            best_epoch = epoch
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }
        print(
            f"epoch={epoch:02d} loss={metrics['training_loss']:.6f} "
            f"top1={metrics['top1_optimal_rate']:.4f} "
            f"regret={metrics['mean_selection_regret']:.4f} device={device}",
            flush=True,
        )

    elapsed = time.perf_counter() - started
    assert best_state is not None and best_metrics is not None
    model.load_state_dict(best_state)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "schema_version": "aura-mps-student/v1",
        "model_state_dict": best_state,
        "input_dim": FEATURE_COUNT,
        "label_mean": label_mean,
        "label_scale": label_scale,
        "best_epoch": best_epoch,
        "validation_metrics": best_metrics,
    }
    torch.save(checkpoint, output_path)
    model_sha256 = sha256(output_path)
    export_path = Path(args.export)
    export_path.parent.mkdir(parents=True, exist_ok=True)
    numpy.savez_compressed(
        export_path,
        **{
            key: value.detach().cpu().numpy()
            for key, value in best_state.items()
        },
        label_mean=numpy.asarray(label_mean, dtype=numpy.float32),
        label_scale=numpy.asarray(label_scale, dtype=numpy.float32),
        input_dim=numpy.asarray(FEATURE_COUNT, dtype=numpy.int64),
    )
    export_sha256 = sha256(export_path)

    primary = training_report["metrics"]["validation"]
    promoted = (
        float(best_metrics["top1_optimal_rate"])
        >= float(primary["top1_optimal_rate"])
        and float(best_metrics["mean_selection_regret"])
        <= float(primary["mean_selection_regret"])
    )
    train_hash = split_hash(train_rows)
    validation_hash = split_hash(validation_rows)
    total_sample_passes = args.samples_per_epoch * args.epochs
    payload = {
        "schema_version": "aura-mps-scale/v1",
        "model_path": display_path(output_path),
        "model_sha256": model_sha256,
        "portable_export_path": display_path(export_path),
        "portable_export_sha256": export_sha256,
        "dataset_provenance": {
            "source": display_path(dataset_path),
            "generator_version": training_report["dataset_generator_version"],
            "unique_train_rows": len(train_rows),
            "unique_train_groups": len(train_groups),
            "unique_validation_rows": len(validation_rows),
            "unique_validation_groups": len(validation_groups),
            "train_sha256": train_hash,
            "validation_sha256": validation_hash,
            "matches_primary_training_report": (
                train_hash == training_report["dataset"]["train_sha256"]
                and validation_hash
                == training_report["dataset"]["validation_sha256"]
            ),
        },
        "training_scale": {
            "sample_passes_per_epoch": args.samples_per_epoch,
            "epochs": args.epochs,
            "total_sample_passes": total_sample_passes,
            "batch_groups": args.batch_groups,
            "rows_per_group": 4,
            "steps_per_epoch": steps_per_epoch,
            "elapsed_seconds": round(elapsed, 6),
            "sample_passes_per_second": round(total_sample_passes / elapsed, 2),
            "unique_candidate_claim": False,
            "interpretation": (
                "Repeated GPU sample-passes over 1,440 unique rollout-labeled train rows; "
                "not 20 million unique candidates."
            ),
        },
        "validation": best_metrics,
        "best_epoch": best_epoch,
        "history": history,
        "primary_extra_trees_comparison": {
            "top1_optimal_rate": primary["top1_optimal_rate"],
            "mean_selection_regret": primary["mean_selection_regret"],
            "mae": primary["mae"],
        },
        "promotion_decision": {
            "candidate_for_closed_loop_promotion": promoted,
            "promote_to_agent_runtime": False,
            "selected_runtime_backend": "sklearn_extra_trees_regressor",
            "criterion": (
                "Validation promotion requires MLP top-1 and regret to beat ExtraTrees. "
                "Runtime promotion additionally requires a new seed-disjoint closed-loop comparison."
            ),
        },
        "runtime": {
            "device": str(device),
            "mps_built": torch.backends.mps.is_built(),
            "mps_available": torch.backends.mps.is_available(),
            "torch": torch.__version__,
            "python": platform.python_version(),
            "machine": platform.machine(),
        },
        "limitations": [
            "The GPU run reuses 1,440 unique rollout-labeled rows; scale is sample-pass throughput, not new ground truth.",
            "Validation remains synthetic simulator evidence, not operational SATCOM accuracy.",
            "The MPS model is optional and is not promoted when action ranking is worse than ExtraTrees.",
        ],
        "safety_boundary": {
            "synthetic_mission_effects_only": True,
            "exploit_code": False,
            "operational_rf_parameters": False,
            "live_network_actions": False,
        },
    }
    metrics_path = Path(args.metrics)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps({"validation": best_metrics, "promotion": payload["promotion_decision"]}, indent=2))
    print(f"model: {output_path}")
    print(f"portable export: {export_path}")
    print(f"metrics: {metrics_path}")


def choose_device(requested: str) -> torch.device:
    if requested == "auto":
        return torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    if requested == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS requested but is not available")
    return torch.device(requested)


def validate_dataset(
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    report: dict[str, Any],
) -> None:
    if len(train_rows) != 1440 or len(validation_rows) != 576:
        raise ValueError("rollout dataset row count differs from primary training evidence")
    if any(len(row["features"]) != FEATURE_COUNT for row in train_rows + validation_rows):
        raise ValueError("rollout dataset feature count mismatch")
    if split_hash(train_rows) != report["dataset"]["train_sha256"]:
        raise ValueError("GPU train split hash differs from primary model evidence")
    if split_hash(validation_rows) != report["dataset"]["validation_sha256"]:
        raise ValueError("GPU validation split hash differs from primary model evidence")


def materialize_groups(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["group_id"])].append(row)
    groups = []
    for group_id in sorted(grouped):
        group = grouped[group_id]
        if len(group) != 4:
            raise ValueError(f"group {group_id} must contain four candidates")
        groups.append(group)
    return groups


def predict_rows(
    model: nn.Module,
    rows: list[dict[str, Any]],
    device: torch.device,
    label_mean: float,
    label_scale: float,
) -> list[float]:
    model.eval()
    features = torch.tensor(
        [row["features"] for row in rows],
        dtype=torch.float32,
        device=device,
    )
    with torch.no_grad():
        standardized = model(features)
        predictions = standardized * label_scale + label_mean
    return [float(value) for value in predictions.cpu().tolist()]


def evaluate_predictions(
    rows: list[dict[str, Any]],
    predictions: list[float],
) -> dict[str, float | int]:
    labels = [float(row["label_incremental_impact"]) for row in rows]
    grouped: dict[str, list[tuple[dict[str, Any], float]]] = defaultdict(list)
    for row, prediction in zip(rows, predictions):
        grouped[str(row["group_id"])].append((row, prediction))
    regrets = []
    exact = 0
    optimal = 0
    for group in grouped.values():
        predicted_row = max(group, key=lambda item: item[1])[0]
        actual_row = max(
            group,
            key=lambda item: float(item[0]["label_incremental_impact"]),
        )[0]
        regret = max(
            0.0,
            float(actual_row["label_incremental_impact"])
            - float(predicted_row["label_incremental_impact"]),
        )
        regrets.append(regret)
        optimal += int(regret <= 0.01)
        exact += int(predicted_row["action"] == actual_row["action"])

    squared_errors = [
        (label - prediction) ** 2
        for label, prediction in zip(labels, predictions)
    ]
    absolute_errors = [
        abs(label - prediction)
        for label, prediction in zip(labels, predictions)
    ]
    label_mean = mean(labels)
    total_variance = sum((label - label_mean) ** 2 for label in labels)
    residual = sum(squared_errors)
    return {
        "rows": len(rows),
        "groups": len(grouped),
        "top1_optimal_rate": round(optimal / len(grouped), 6),
        "exact_top1_action_match_rate": round(exact / len(grouped), 6),
        "mean_selection_regret": round(mean(regrets), 6),
        "p95_selection_regret": round(sorted(regrets)[int(0.95 * len(regrets))], 6),
        "mae": round(mean(absolute_errors), 6),
        "rmse": round(math.sqrt(mean(squared_errors)), 6),
        "r2": round(1.0 - residual / max(total_variance, 1e-12), 6),
    }


def model_order(metrics: dict[str, float | int]) -> tuple[float, float, float]:
    return (
        float(metrics["mean_selection_regret"]),
        -float(metrics["top1_optimal_rate"]),
        float(metrics["mae"]),
    )


def split_hash(rows: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        payload = {key: value for key, value in row.items() if key != "split"}
        digest.update(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        digest.update(b"\n")
    return digest.hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
