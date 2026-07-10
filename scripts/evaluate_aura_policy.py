from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import joblib
import numpy
import sklearn

from src.tsra_agent.attack_ml_policy import (
    ATTACK_FEATURE_NAMES,
    DEFAULT_ATTACK_CONFIG_PATH,
    DEFAULT_ATTACK_MODEL_PATH,
    AblatedAttackImpactModel,
    attack_model_backend_name,
    load_attack_model,
)
from src.tsra_agent.ml_policy import DEFAULT_SKLEARN_MODEL_PATH, load_sklearn_model
from src.tsra_agent.models import AttackMode
from src.tsra_agent.simulator import MissionSimulator


DEFAULT_HOLDOUT_SEEDS = (
    "2003,2011,2017,2027,2029,2039,2053,2063,2069,2081,2083,2087,2089,2099,"
    "2111,2113,2129,2131,2137,2141,2143,2153,2161,2179,2203,2207,2213,2221,2237,2239"
)
DEVELOPMENT_SEEDS = [1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181]
DEFAULT_CONTEXTS = "none,rule,tsra,ml"
METRIC_NAMES = [
    "mission_impact_score",
    "p95_critical_latency",
    "stale_data_ratio",
    "priority_inversion_rate",
    "lost_messages",
    "backlog_messages",
    "expired_messages",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate AURA rule, learned, and zero-model policies on unseen seeds."
    )
    parser.add_argument("--seeds", default=DEFAULT_HOLDOUT_SEEDS)
    parser.add_argument("--contexts", default=DEFAULT_CONTEXTS)
    parser.add_argument("--ticks", type=int, default=180)
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument(
        "--output",
        default="examples/aura_ml_holdout_30_seed_summary.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seeds = parse_ints(args.seeds)
    contexts = parse_strings(args.contexts)
    if args.ticks < 60:
        raise ValueError("holdout evaluation requires at least 60 ticks")
    invalid_contexts = set(contexts) - {"none", "rule", "tsra", "ml"}
    if invalid_contexts:
        raise ValueError(f"unsupported defense contexts: {sorted(invalid_contexts)}")

    training = read_json(ROOT / "models" / "aura_rollout_training_report.json")
    training_seeds = set(training["split_contract"]["train_seeds"])
    validation_seeds = set(training["split_contract"]["validation_seeds"])
    forbidden = training_seeds | validation_seeds | set(DEVELOPMENT_SEEDS)
    overlap = sorted(set(seeds) & forbidden)
    if overlap:
        raise ValueError(f"holdout seeds overlap model/development seeds: {overlap}")

    attack_model = load_attack_model()
    if hasattr(attack_model, "n_jobs"):
        if int(attack_model.n_jobs) != 1:
            raise ValueError("bundled AURA model must use n_jobs=1 for bounded inference")
    defense_model = load_sklearn_model() if "ml" in contexts else None
    raw: dict[str, list[dict[str, Any]]] = {context: [] for context in contexts}

    for context in contexts:
        for index, seed in enumerate(seeds, start=1):
            record = evaluate_seed(
                seed,
                context,
                args.ticks,
                attack_model,
                defense_model,
            )
            raw[context].append(record)
            if index % 5 == 0 or index == len(seeds):
                print(
                    f"{context}: seeds {index}/{len(seeds)}",
                    flush=True,
                )

    conditions = {
        context: summarize_context(
            records,
            bootstrap_samples=args.bootstrap_samples,
            bootstrap_seed=20260710 + index,
        )
        for index, (context, records) in enumerate(raw.items())
    }
    defended_contexts = [context for context in contexts if context != "none"]
    acceptance = {
        "positive_mean_vs_rule_all_contexts": all(
            conditions[context]["paired_ml_minus_rule"]["mean"] > 0.0
            for context in contexts
        ),
        "positive_ci_vs_rule_defended_contexts": all(
            conditions[context]["paired_ml_minus_rule"]["bootstrap_95_ci"][0] > 0.0
            for context in defended_contexts
        ),
        "positive_ci_vs_zero_model_all_contexts": all(
            conditions[context]["paired_ml_minus_zero_model"]["bootstrap_95_ci"][0] > 0.0
            for context in contexts
        ),
        "model_influenced_actions_observed": all(
            conditions[context]["aura_ml_agent"]["model_influenced_ticks"]["mean"] > 0.0
            for context in contexts
        ),
    }
    acceptance["closed_loop_holdout_pass"] = all(acceptance.values())

    output_path = Path(args.output)
    payload = {
        "schema_version": "aura-ml-holdout/v1",
        "created_by": "scripts/evaluate_aura_policy.py",
        "scenario": AttackMode.HYBRID.value,
        "ticks": args.ticks,
        "seeds": seeds,
        "seed_count": len(seeds),
        "contexts": contexts,
        "seed_provenance": {
            "model_train_seeds": sorted(training_seeds),
            "model_validation_seeds": sorted(validation_seeds),
            "policy_development_seeds": DEVELOPMENT_SEEDS,
            "holdout_overlap": overlap,
        },
        "model_provenance": {
            "path": display_path(DEFAULT_ATTACK_MODEL_PATH),
            "sha256": sha256(DEFAULT_ATTACK_MODEL_PATH),
            "training_report_sha256": sha256(
                ROOT / "models" / "aura_rollout_training_report.json"
            ),
            "config_path": display_path(DEFAULT_ATTACK_CONFIG_PATH),
            "config_sha256": sha256(DEFAULT_ATTACK_CONFIG_PATH),
            "backend": attack_model_backend_name(attack_model),
            "feature_count": len(ATTACK_FEATURE_NAMES),
            "defense_model_sha256": sha256(DEFAULT_SKLEARN_MODEL_PATH),
        },
        "conditions": conditions,
        "acceptance": acceptance,
        "interpretation": (
            "Higher mission impact is better for AURA. Paired differences use the same "
            "seed and defense context. Bootstrap intervals resample seeds, not rows."
        ),
        "limitations": [
            "All outcomes are from the closed synthetic mission-event simulator.",
            "The holdout is independent by seed but not an operational SATCOM field test.",
            "Defense contexts for one seed are correlated and are reported separately.",
        ],
        "runtime": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": numpy.__version__,
            "joblib": joblib.__version__,
        },
        "safety_boundary": {
            "synthetic_mission_effects_only": True,
            "exploit_code": False,
            "operational_rf_parameters": False,
            "live_network_actions": False,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps({"acceptance": acceptance}, indent=2))
    print(f"output: {output_path}")


def evaluate_seed(
    seed: int,
    context: str,
    ticks: int,
    attack_model: object,
    defense_model: object | None,
) -> dict[str, Any]:
    defense_enabled = context != "none"
    defense_mode = "tsra" if context == "none" else context
    shared = {
        "ticks": ticks,
        "seed": seed,
        "attack_mode": AttackMode.HYBRID,
        "defense_enabled": defense_enabled,
        "defense_mode": defense_mode,
        "sklearn_model": defense_model if context == "ml" else None,
        "retain_agent_traces": False,
    }
    rule_simulator = MissionSimulator(**shared)
    rule = rule_simulator.run("aura_rule")
    ml_simulator = MissionSimulator(
        **shared,
        attack_policy="ml",
        attack_model=attack_model,
    )
    ml = ml_simulator.run("aura_ml")
    zero_simulator = MissionSimulator(
        **shared,
        attack_policy="ml",
        attack_model=AblatedAttackImpactModel(),
    )
    zero = zero_simulator.run("aura_zero_model")
    return {
        "seed": seed,
        "rule": select_metrics(rule.metrics.as_dict()),
        "ml": select_metrics(ml.metrics.as_dict()),
        "zero_model": select_metrics(zero.metrics.as_dict()),
        "ml_agent": {
            "action_counts": dict(ml_simulator.red.action_counts),
            "selection_source_counts": dict(
                ml_simulator.red.selection_source_counts
            ),
            "model_influenced_ticks": ml_simulator.red.model_influenced_ticks,
            "model_changed_rule_ticks": ml_simulator.red.model_changed_rule_ticks,
        },
        "zero_agent": {
            "action_counts": dict(zero_simulator.red.action_counts),
            "model_influenced_ticks": zero_simulator.red.model_influenced_ticks,
        },
    }


def summarize_context(
    records: list[dict[str, Any]],
    *,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    rule = aggregate_metric_rows([record["rule"] for record in records])
    ml = aggregate_metric_rows([record["ml"] for record in records])
    zero = aggregate_metric_rows([record["zero_model"] for record in records])
    rule_differences = [
        record["ml"]["mission_impact_score"]
        - record["rule"]["mission_impact_score"]
        for record in records
    ]
    zero_differences = [
        record["ml"]["mission_impact_score"]
        - record["zero_model"]["mission_impact_score"]
        for record in records
    ]
    action_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    for record in records:
        action_counts.update(record["ml_agent"]["action_counts"])
        source_counts.update(record["ml_agent"]["selection_source_counts"])
    return {
        "rule_aura": rule,
        "aura_ml": ml,
        "aura_ml_zero_model": zero,
        "paired_ml_minus_rule": paired_summary(
            rule_differences,
            bootstrap_samples=bootstrap_samples,
            seed=bootstrap_seed,
        ),
        "paired_ml_minus_zero_model": paired_summary(
            zero_differences,
            bootstrap_samples=bootstrap_samples,
            seed=bootstrap_seed + 100,
        ),
        "aura_ml_agent": {
            "action_counts": dict(sorted(action_counts.items())),
            "selection_source_counts": dict(sorted(source_counts.items())),
            "model_influenced_ticks": aggregate_values(
                [record["ml_agent"]["model_influenced_ticks"] for record in records]
            ),
            "model_changed_rule_ticks": aggregate_values(
                [record["ml_agent"]["model_changed_rule_ticks"] for record in records]
            ),
        },
    }


def paired_summary(
    differences: list[float],
    *,
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Any]:
    interval = bootstrap_mean_interval(
        differences,
        samples=bootstrap_samples,
        seed=seed,
    )
    return {
        "mean": round(mean(differences), 4),
        "stdev": round(pstdev(differences), 4),
        "bootstrap_95_ci": interval,
        "wins": sum(value > 1e-9 for value in differences),
        "ties": sum(abs(value) <= 1e-9 for value in differences),
        "losses": sum(value < -1e-9 for value in differences),
        "count": len(differences),
        "minimum": round(min(differences), 4),
        "maximum": round(max(differences), 4),
    }


def bootstrap_mean_interval(
    values: list[float],
    *,
    samples: int,
    seed: int,
) -> list[float]:
    if samples < 1000:
        raise ValueError("bootstrap requires at least 1000 samples")
    rng = random.Random(seed)
    estimates = []
    for _ in range(samples):
        estimates.append(mean(rng.choice(values) for _ in values))
    estimates.sort()
    lower = estimates[int(0.025 * samples)]
    upper = estimates[min(samples - 1, int(0.975 * samples))]
    return [round(lower, 4), round(upper, 4)]


def aggregate_metric_rows(rows: list[dict[str, float]]) -> dict[str, Any]:
    return {
        name: aggregate_values([float(row[name]) for row in rows])
        for name in METRIC_NAMES
    }


def aggregate_values(values: list[float]) -> dict[str, float | int]:
    return {
        "mean": round(mean(values), 4),
        "stdev": round(pstdev(values), 4),
        "count": len(values),
    }


def select_metrics(metrics: dict[str, Any]) -> dict[str, float]:
    return {name: float(metrics[name]) for name in METRIC_NAMES}


def parse_ints(value: str) -> list[int]:
    values = [int(part.strip()) for part in value.split(",") if part.strip()]
    if not values:
        raise ValueError("seed list must not be empty")
    if len(set(values)) != len(values):
        raise ValueError("holdout seeds must be unique")
    return values


def parse_strings(value: str) -> list[str]:
    values = [part.strip() for part in value.split(",") if part.strip()]
    if not values:
        raise ValueError("context list must not be empty")
    return values


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
