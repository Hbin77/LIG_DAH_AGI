from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import joblib
import numpy
import sklearn
from joblib import dump
from sklearn.base import clone
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold

from src.tsra_agent.agents import AURALite
from src.tsra_agent.attack_ml_policy import (
    ATTACK_FEATURE_NAMES,
    DEFAULT_ATTACK_CONFIG_PATH,
    DEFAULT_ATTACK_MODEL_PATH,
    attack_candidate_features,
)
from src.tsra_agent.ml_policy import load_sklearn_model
from src.tsra_agent.models import AttackMode
from src.tsra_agent.simulator import MissionSimulator


DEFAULT_TRAIN_SEEDS = "1009,1013,1019,1021,1031,1033,1039,1049,1051,1061"
DEFAULT_VALIDATION_SEEDS = "1063,1069,1087,1091"
DEFAULT_TARGET_TICKS = "35,45,55,77,87,97,119,129,139"
DEFAULT_CONTEXTS = "none,rule,tsra,ml"
DEFAULT_BEHAVIORS = "rule"
DATASET_GENERATOR_VERSION = "counterfactual-rollout-v1"


class CachedProbabilityModel:
    """Shares exact defense-model predictions across paired rollout branches."""

    def __init__(self, model: object) -> None:
        self.model = model
        self.cache: dict[tuple[float, ...], tuple[float, float]] = {}

    def predict_proba(self, rows: list[list[float]]) -> list[list[float]]:
        result = []
        for row in rows:
            key = tuple(float(value) for value in row)
            probabilities = self.cache.get(key)
            if probabilities is None:
                raw = self.model.predict_proba([row])[0]
                probabilities = (float(raw[0]), float(raw[1]))
                self.cache[key] = probabilities
            result.append([probabilities[0], probabilities[1]])
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train AURA-ML on paired counterfactual mission-simulator rollouts."
    )
    parser.add_argument("--train-seeds", default=DEFAULT_TRAIN_SEEDS)
    parser.add_argument("--validation-seeds", default=DEFAULT_VALIDATION_SEEDS)
    parser.add_argument("--target-ticks", default=DEFAULT_TARGET_TICKS)
    parser.add_argument("--contexts", default=DEFAULT_CONTEXTS)
    parser.add_argument("--behaviors", default=DEFAULT_BEHAVIORS)
    parser.add_argument("--horizon", type=int, default=30)
    parser.add_argument("--commitment-ticks", type=int, default=4)
    parser.add_argument("--expected-ticks", type=int, default=180)
    parser.add_argument("--output", default=str(DEFAULT_ATTACK_MODEL_PATH))
    parser.add_argument("--config", default=str(DEFAULT_ATTACK_CONFIG_PATH))
    parser.add_argument("--report", default="models/aura_rollout_training_report.json")
    parser.add_argument(
        "--dataset-output",
        default="outputs/datasets/aura_counterfactual_rollouts.jsonl",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train_seeds = parse_ints(args.train_seeds)
    validation_seeds = parse_ints(args.validation_seeds)
    target_ticks = parse_ints(args.target_ticks)
    contexts = parse_strings(args.contexts)
    behaviors = parse_strings(args.behaviors)
    validate_inputs(
        train_seeds,
        validation_seeds,
        target_ticks,
        contexts,
        behaviors,
        args.horizon,
        args.commitment_ticks,
    )

    defense_model = (
        CachedProbabilityModel(load_sklearn_model())
        if "ml" in contexts
        else None
    )
    print("Generating train counterfactual rollouts...", flush=True)
    train_rows = generate_rollout_rows(
        train_seeds,
        target_ticks,
        contexts,
        behaviors,
        horizon=args.horizon,
        commitment_ticks=args.commitment_ticks,
        expected_ticks=args.expected_ticks,
        defense_model=defense_model,
    )
    print("Generating validation counterfactual rollouts...", flush=True)
    validation_rows = generate_rollout_rows(
        validation_seeds,
        target_ticks,
        contexts,
        behaviors,
        horizon=args.horizon,
        commitment_ticks=args.commitment_ticks,
        expected_ticks=args.expected_ticks,
        defense_model=defense_model,
    )

    candidates = model_candidates()
    cv_results = cross_validate_models(candidates, train_rows)
    best_name = min(
        cv_results,
        key=lambda name: (
            cv_results[name]["mean_selection_regret"],
            -cv_results[name]["top1_optimal_rate"],
            cv_results[name]["mae"],
        ),
    )
    model = candidates[best_name]
    model.fit(
        [row["features"] for row in train_rows],
        [row["label_incremental_impact"] for row in train_rows],
    )
    train_predictions = [
        float(value) for value in model.predict([row["features"] for row in train_rows])
    ]
    validation_predictions = [
        float(value)
        for value in model.predict([row["features"] for row in validation_rows])
    ]
    train_metrics = evaluate_predictions(train_rows, train_predictions)
    validation_metrics = evaluate_predictions(validation_rows, validation_predictions)
    validation_rule = evaluate_predictions(
        validation_rows,
        [float(row["rule_score"]) for row in validation_rows],
        include_regression=False,
    )
    validation_zero = evaluate_predictions(
        validation_rows,
        [0.0 for _ in validation_rows],
        include_regression=False,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, output_path)
    model_sha256 = sha256(output_path)
    config_path = Path(args.config)
    config_payload = {
        "schema_version": "aura-ml-policy-config/v1",
        "model_path": display_path(output_path),
        "model_sha256": model_sha256,
        "config": {
            "detectability_weight": 0.05,
            "repeated_tactic_penalty": 0.03,
            "minimum_predicted_impact": 0.02,
            "commitment_ticks": float(args.commitment_ticks),
        },
    }
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(config_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    dataset_path = Path(args.dataset_output)
    write_dataset(dataset_path, train_rows, validation_rows)
    train_hash = dataset_sha256(train_rows)
    validation_hash = dataset_sha256(validation_rows)
    report = {
        "schema_version": "aura-rollout-training/v1",
        "dataset_generator_version": DATASET_GENERATOR_VERSION,
        "model_path": display_path(output_path),
        "model_sha256": model_sha256,
        "config_path": display_path(config_path),
        "selected_model": best_name,
        "feature_names": ATTACK_FEATURE_NAMES,
        "feature_count": len(ATTACK_FEATURE_NAMES),
        "label_definition": (
            "Paired mission-impact delta versus a four-tick no-op commitment from the "
            "same seed, defense context, prefix behavior, and decision tick."
        ),
        "rollout_contract": {
            "scenario": AttackMode.HYBRID.value,
            "horizon_ticks": args.horizon,
            "commitment_ticks": args.commitment_ticks,
            "target_ticks": target_ticks,
            "defense_contexts": contexts,
            "prefix_behaviors": behaviors,
            "common_random_seed_within_group": True,
        },
        "split_contract": {
            "split_unit": "simulator seed",
            "train_seeds": train_seeds,
            "validation_seeds": validation_seeds,
            "seed_overlap": sorted(set(train_seeds) & set(validation_seeds)),
            "row_random_split": False,
            "model_selection": "GroupKFold by simulator seed on train split only",
        },
        "dataset": {
            "train_sha256": train_hash,
            "validation_sha256": validation_hash,
            "train": profile_rows(train_rows),
            "validation": profile_rows(validation_rows),
            "generated_jsonl": display_path(dataset_path),
            "generated_jsonl_tracked": False,
        },
        "model_selection_cv": cv_results,
        "metrics": {
            "train": train_metrics,
            "validation": validation_metrics,
            "validation_rule_ranker": validation_rule,
            "validation_zero_model": validation_zero,
        },
        "runtime": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": numpy.__version__,
            "joblib": joblib.__version__,
        },
        "limitations": [
            "Labels come from the closed synthetic simulator, not operational SATCOM data.",
            "Validation seeds are independent, but they use the same simulator implementation.",
            "The model predicts a bounded four-tick macro-action effect, not an RF outcome.",
            "Closed-loop policy value requires a separate post-training holdout experiment.",
        ],
        "safety_boundary": {
            "synthetic_mission_effects_only": True,
            "exploit_code": False,
            "operational_rf_parameters": False,
            "live_network_actions": False,
        },
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(json.dumps({"selected_model": best_name, "validation": validation_metrics}, indent=2))
    print(f"model: {output_path}")
    print(f"report: {report_path}")
    print(f"dataset: {dataset_path}")


def generate_rollout_rows(
    seeds: list[int],
    target_ticks: list[int],
    contexts: list[str],
    behaviors: list[str],
    *,
    horizon: int,
    commitment_ticks: int,
    expected_ticks: int,
    defense_model: object | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total_groups = len(seeds) * len(contexts) * len(behaviors) * len(target_ticks)
    completed = 0
    for seed in seeds:
        for context in contexts:
            for behavior in behaviors:
                for target_tick in target_ticks:
                    prefix = prefix_overrides(behavior, target_tick)
                    reference = build_simulator(
                        ticks=target_tick + 1,
                        seed=seed,
                        context=context,
                        overrides=prefix,
                        defense_model=defense_model,
                    )
                    reference.run("aura_rollout_reference")
                    state = reference.observed_states[target_tick]
                    candidates = [
                        candidate
                        for candidate in AURALite(AttackMode.HYBRID).rank_candidates(state)
                        if candidate["eligible"]
                    ]
                    outcomes: dict[str, float] = {}
                    for candidate in candidates:
                        action = AttackMode(candidate["action"])
                        overrides = dict(prefix)
                        overrides.update(
                            {
                                tick: action
                                for tick in range(
                                    target_tick,
                                    target_tick + commitment_ticks,
                                )
                            }
                        )
                        rollout = build_simulator(
                            ticks=target_tick + horizon,
                            seed=seed,
                            context=context,
                            overrides=overrides,
                            defense_model=defense_model,
                        ).run("aura_counterfactual_rollout")
                        outcomes[action.value] = rollout.metrics.mission_impact_score

                    no_op_impact = outcomes[AttackMode.NONE.value]
                    group_id = f"{seed}:{context}:{behavior}:{target_tick}"
                    for candidate in candidates:
                        action = str(candidate["action"])
                        rows.append(
                            {
                                "group_id": group_id,
                                "seed": seed,
                                "defense_context": context,
                                "prefix_behavior": behavior,
                                "target_tick": target_tick,
                                "action": action,
                                "target_link": str(candidate["target_link"]),
                                "rule_score": float(candidate["score"]),
                                "outcome_mission_impact": outcomes[action],
                                "no_op_mission_impact": no_op_impact,
                                "label_incremental_impact": round(
                                    outcomes[action] - no_op_impact,
                                    6,
                                ),
                                "features": attack_candidate_features(
                                    state,
                                    candidate,
                                    expected_ticks=expected_ticks,
                                ),
                            }
                        )
                    completed += 1
                    if completed % 25 == 0 or completed == total_groups:
                        print(
                            f"  rollout groups {completed}/{total_groups}",
                            flush=True,
                        )
    return rows


def build_simulator(
    *,
    ticks: int,
    seed: int,
    context: str,
    overrides: dict[int, AttackMode],
    defense_model: object | None,
) -> MissionSimulator:
    defense_enabled = context != "none"
    defense_mode = "tsra" if context == "none" else context
    return MissionSimulator(
        ticks=ticks,
        seed=seed,
        attack_mode=AttackMode.HYBRID,
        defense_enabled=defense_enabled,
        defense_mode=defense_mode,
        sklearn_model=defense_model if context == "ml" else None,
        attack_overrides=overrides,
        retain_agent_traces=False,
    )


def prefix_overrides(behavior: str, target_tick: int) -> dict[int, AttackMode]:
    if behavior == "rule":
        return {}
    mode = AttackMode(behavior)
    return {tick: mode for tick in range(target_tick)}


def model_candidates() -> dict[str, object]:
    return {
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            max_iter=320,
            learning_rate=0.055,
            max_leaf_nodes=31,
            min_samples_leaf=10,
            l2_regularization=0.10,
            random_state=20260710,
        ),
        "extra_trees": ExtraTreesRegressor(
            n_estimators=320,
            min_samples_leaf=2,
            max_features=0.85,
            random_state=20260710,
            n_jobs=1,
        ),
    }


def cross_validate_models(
    candidates: dict[str, object],
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    seeds = sorted({int(row["seed"]) for row in rows})
    split_count = min(5, len(seeds))
    if split_count < 2:
        raise ValueError("at least two train seeds are required for grouped model selection")
    x = [row["features"] for row in rows]
    y = [row["label_incremental_impact"] for row in rows]
    groups = [row["seed"] for row in rows]
    splitter = GroupKFold(n_splits=split_count)
    result: dict[str, dict[str, float]] = {}
    for name, estimator in candidates.items():
        fold_metrics = []
        for train_indices, valid_indices in splitter.split(x, y, groups):
            fitted = clone(estimator)
            fitted.fit([x[index] for index in train_indices], [y[index] for index in train_indices])
            valid_rows = [rows[index] for index in valid_indices]
            predictions = [
                float(value)
                for value in fitted.predict([x[index] for index in valid_indices])
            ]
            fold_metrics.append(evaluate_predictions(valid_rows, predictions))
        result[name] = {
            "folds": float(split_count),
            "mae": round(mean(metric["mae"] for metric in fold_metrics), 6),
            "top1_optimal_rate": round(
                mean(metric["top1_optimal_rate"] for metric in fold_metrics),
                6,
            ),
            "mean_selection_regret": round(
                mean(metric["mean_selection_regret"] for metric in fold_metrics),
                6,
            ),
        }
    return result


def evaluate_predictions(
    rows: list[dict[str, Any]],
    predictions: list[float],
    *,
    include_regression: bool = True,
) -> dict[str, float | int | None]:
    if len(rows) != len(predictions):
        raise ValueError("prediction count must match dataset row count")
    grouped: dict[str, list[tuple[dict[str, Any], float]]] = defaultdict(list)
    for row, prediction in zip(rows, predictions):
        grouped[str(row["group_id"])].append((row, prediction))

    regrets = []
    optimal = 0
    exact = 0
    selected_counts: Counter[str] = Counter()
    for group_rows in grouped.values():
        predicted_row, _ = max(group_rows, key=lambda item: item[1])
        actual_row, _ = max(
            group_rows,
            key=lambda item: float(item[0]["label_incremental_impact"]),
        )
        best_label = float(actual_row["label_incremental_impact"])
        selected_label = float(predicted_row["label_incremental_impact"])
        regret = max(0.0, best_label - selected_label)
        regrets.append(regret)
        optimal += int(regret <= 0.01)
        exact += int(predicted_row["action"] == actual_row["action"])
        selected_counts[str(predicted_row["action"])] += 1

    labels = [float(row["label_incremental_impact"]) for row in rows]
    ordered_regrets = sorted(regrets)
    result: dict[str, float | int | None] = {
        "rows": len(rows),
        "groups": len(grouped),
        "top1_optimal_rate": round(optimal / max(1, len(grouped)), 6),
        "exact_top1_action_match_rate": round(exact / max(1, len(grouped)), 6),
        "mean_selection_regret": round(mean(regrets), 6),
        "p95_selection_regret": round(
            ordered_regrets[min(len(ordered_regrets) - 1, int(0.95 * len(ordered_regrets)))],
            6,
        ),
        "selected_no_op_rate": round(
            selected_counts[AttackMode.NONE.value] / max(1, len(grouped)),
            6,
        ),
    }
    if include_regression:
        result.update(
            {
                "mae": round(float(mean_absolute_error(labels, predictions)), 6),
                "rmse": round(float(mean_squared_error(labels, predictions) ** 0.5), 6),
                "r2": round(float(r2_score(labels, predictions)), 6),
            }
        )
    else:
        result.update({"mae": None, "rmse": None, "r2": None})
    return result


def profile_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [float(row["label_incremental_impact"]) for row in rows]
    features = [row["features"] for row in rows]
    ordered = sorted(labels)
    action_counts = Counter(str(row["action"]) for row in rows)
    group_counts = Counter(str(row["group_id"]) for row in rows)
    feature_groups: dict[tuple[float, ...], list[float]] = defaultdict(list)
    for row in rows:
        feature_groups[tuple(float(value) for value in row["features"])].append(
            float(row["label_incremental_impact"])
        )
    duplicate_feature_groups = {
        features: group_labels
        for features, group_labels in feature_groups.items()
        if len(group_labels) > 1
    }
    conflicting_feature_groups = {
        features: group_labels
        for features, group_labels in duplicate_feature_groups.items()
        if len(set(group_labels)) > 1
    }
    conflicting_rows = sum(len(values) for values in conflicting_feature_groups.values())
    return {
        "grain": "one candidate action in one paired counterfactual rollout group",
        "rows": len(rows),
        "groups": len(group_counts),
        "seeds": sorted({int(row["seed"]) for row in rows}),
        "feature_columns": len(ATTACK_FEATURE_NAMES),
        "missing_value_count": sum(
            value is None for row in features for value in row
        ),
        "out_of_range_feature_count": sum(
            float(value) < 0.0 or float(value) > 1.0
            for row in features
            for value in row
        ),
        "exact_duplicate_feature_rows": len(features)
        - len({tuple(float(value) for value in row) for row in features}),
        "duplicate_feature_groups": len(duplicate_feature_groups),
        "conflicting_duplicate_feature_groups": len(conflicting_feature_groups),
        "conflicting_duplicate_feature_rows": conflicting_rows,
        "conflicting_duplicate_feature_row_rate": round(
            conflicting_rows / len(rows),
            6,
        ),
        "maximum_conflicting_label_range": round(
            max(
                (
                    max(values) - min(values)
                    for values in conflicting_feature_groups.values()
                ),
                default=0.0,
            ),
            6,
        ),
        "duplicate_interpretation": (
            "Identical observable state-action features can have different labels because "
            "future packet loss is stochastic and defense policy identity is not exposed to AURA."
        ),
        "group_size_counts": dict(sorted(Counter(group_counts.values()).items())),
        "action_counts": dict(sorted(action_counts.items())),
        "label": {
            "minimum": round(min(labels), 6),
            "p05": quantile(ordered, 0.05),
            "median": quantile(ordered, 0.50),
            "p95": quantile(ordered, 0.95),
            "maximum": round(max(labels), 6),
            "mean": round(mean(labels), 6),
            "zero_rate": round(sum(abs(value) < 1e-9 for value in labels) / len(labels), 6),
            "positive_rate": round(sum(value > 0.0 for value in labels) / len(labels), 6),
            "negative_rate": round(sum(value < 0.0 for value in labels) / len(labels), 6),
        },
    }


def write_dataset(
    path: Path,
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for split, rows in (("train", train_rows), ("validation", validation_rows)):
            for row in rows:
                handle.write(
                    json.dumps(
                        {"split": split, **row},
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                )


def dataset_sha256(rows: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(
            json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        digest.update(b"\n")
    return digest.hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quantile(ordered: list[float], fraction: float) -> float:
    index = min(len(ordered) - 1, int(fraction * (len(ordered) - 1)))
    return round(float(ordered[index]), 6)


def parse_ints(value: str) -> list[int]:
    parsed = [int(part.strip()) for part in value.split(",") if part.strip()]
    if not parsed:
        raise ValueError("integer list must not be empty")
    return parsed


def parse_strings(value: str) -> list[str]:
    parsed = [part.strip() for part in value.split(",") if part.strip()]
    if not parsed:
        raise ValueError("string list must not be empty")
    return parsed


def validate_inputs(
    train_seeds: list[int],
    validation_seeds: list[int],
    target_ticks: list[int],
    contexts: list[str],
    behaviors: list[str],
    horizon: int,
    commitment_ticks: int,
) -> None:
    overlap = set(train_seeds) & set(validation_seeds)
    if overlap:
        raise ValueError(f"train and validation seeds overlap: {sorted(overlap)}")
    if min(target_ticks) < 0:
        raise ValueError("target ticks must be non-negative")
    if horizon <= commitment_ticks:
        raise ValueError("rollout horizon must exceed the action commitment")
    invalid_contexts = set(contexts) - {"none", "rule", "tsra", "ml"}
    if invalid_contexts:
        raise ValueError(f"unsupported defense contexts: {sorted(invalid_contexts)}")
    valid_behaviors = {
        "rule",
        AttackMode.NONE.value,
        AttackMode.LINK_DEGRADATION.value,
        AttackMode.MISSION_AWARE_DELAY.value,
        AttackMode.FAILOVER_CHASING.value,
    }
    invalid_behaviors = set(behaviors) - valid_behaviors
    if invalid_behaviors:
        raise ValueError(f"unsupported prefix behaviors: {sorted(invalid_behaviors)}")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
