from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tsra_agent.evaluator import resilience_gain
from src.tsra_agent.ml_policy import (
    DEFAULT_POLICY_CONFIG_PATH,
    DEFAULT_SKLEARN_MODEL_PATH,
    load_sklearn_model,
    save_policy_config,
)
from src.tsra_agent.models import AttackMode, RunMetrics
from src.tsra_agent.simulator import MissionSimulator


DEFAULT_CONFIG: dict[str, float] = {
    "ml_alert_threshold": 0.50,
    "ml_priority_threshold": 0.42,
    "ml_minimum_mode_threshold": 0.72,
    "ml_pace_threshold": 0.50,
    "ml_stale_badge_threshold": 0.62,
    "ml_quarantine_threshold": 0.78,
    "ml_recovery_threshold": 0.32,
    "ml_weight": 0.65,
    "heuristic_weight": 0.35,
    "recovery_stable_ticks_required": 3,
    "recovery_queue_threshold": 12,
    "recovery_latency_threshold": 6.0,
    "critical_queue_guard_threshold": 0,
    "queue_guard_threshold": 4,
    "satcom_guard_threshold": 0.92,
    "satcom_return_health_threshold": 0.86,
    "satcom_return_risk_threshold": 0.50,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tune TSRA-ML guardrail policy on the mission simulator.")
    parser.add_argument("--candidates", type=int, default=96)
    parser.add_argument("--ticks", type=int, default=180)
    parser.add_argument("--seed", type=int, default=20260709)
    parser.add_argument("--tune-seeds", default="7,11,19,23,31")
    parser.add_argument("--validation-seeds", default="41,43,47")
    parser.add_argument("--output", default=str(DEFAULT_POLICY_CONFIG_PATH))
    parser.add_argument("--report", default="models/tsra_ml_tuning_report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    tune_seeds = parse_seeds(args.tune_seeds)
    validation_seeds = parse_seeds(args.validation_seeds)
    sklearn_model = load_sklearn_model()

    tune_refs = build_reference_runs(args.ticks, tune_seeds)
    validation_refs = build_reference_runs(args.ticks, validation_seeds)
    candidate_results = []
    best: dict[str, Any] | None = None

    for index, config in enumerate(generate_candidates(rng, args.candidates), start=1):
        evaluation = evaluate_config(config, args.ticks, tune_refs, sklearn_model)
        record = {
            "rank_input_order": index,
            "objective": evaluation["objective"],
            "config": config,
            "metrics": evaluation["metrics"],
        }
        candidate_results.append(record)
        if best is None or evaluation["objective"] < best["objective"]:
            best = record

    assert best is not None
    validation = evaluate_config(best["config"], args.ticks, validation_refs, sklearn_model)
    validation_metrics = validation["metrics"]
    if validation_metrics["missing_model_influence_seed_count"] != 0:
        raise RuntimeError("selected policy has a validation seed with no learned-model influence")
    if validation_metrics["guarded_model_influenced_ticks"] != 0:
        raise RuntimeError("selected policy has learned-model influence under no attack")
    output_path = Path(args.output)
    report_path = Path(args.report)
    save_policy_config(best["config"], output_path)
    model_sha256 = hashlib.sha256(DEFAULT_SKLEARN_MODEL_PATH.read_bytes()).hexdigest()
    config_sha256 = hashlib.sha256(output_path.read_bytes()).hexdigest()

    top_candidates = sorted(candidate_results, key=lambda item: item["objective"])[:10]
    report = {
        "schema_version": "tsra-ml-policy-tuning/v2",
        "method": "Randomized guardrail threshold search scored by mission-impact simulation.",
        "ticks": args.ticks,
        "random_seed": args.seed,
        "candidate_count": len(candidate_results),
        "tune_seeds": tune_seeds,
        "validation_seeds": validation_seeds,
        "selected_policy_config_path": display_path(output_path),
        "selected_policy_config_sha256": config_sha256,
        "model_provenance": {
            "path": display_path(DEFAULT_SKLEARN_MODEL_PATH),
            "sha256": model_sha256,
            "training_report": "models/tsra_sklearn_training_report.json",
        },
        "selected_config": best["config"],
        "tune_result": {
            "objective": best["objective"],
            "metrics": best["metrics"],
        },
        "validation_result": validation,
        "top_candidates": top_candidates,
        "objective_definition": {
            "direction": "lower_is_better",
            "terms": [
                "mean mission_impact_score",
                "priority inversion penalty",
                "stale ratio penalty",
                "false alarm penalty",
                "missing detection/recovery penalty",
                "excessive video deferral penalty",
                "excessive compressed snapshot penalty",
                "planned stale noncritical shedding penalty",
                "defense intervention cost",
                "priority-boost control cost",
                "no-attack intervention cost",
                "missing closed-loop model influence penalty",
                "no-attack model influence penalty",
            ],
        },
        "safety_boundary": {
            "synthetic_mission_event_simulator_only": True,
            "exploit_code": False,
            "operational_rf_parameters": False,
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["tune_result"], indent=2, ensure_ascii=False))
    print(json.dumps({"validation_result": validation}, indent=2, ensure_ascii=False))
    print(f"policy_config: {output_path}")
    print(f"report: {report_path}")


def parse_seeds(value: str) -> list[int]:
    seeds = [int(part.strip()) for part in value.split(",") if part.strip()]
    if not seeds:
        raise ValueError("seed list must contain at least one integer")
    return seeds


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def build_reference_runs(ticks: int, seeds: list[int]) -> dict[int, dict[str, RunMetrics]]:
    refs = {}
    for seed in seeds:
        baseline = MissionSimulator(ticks, seed, AttackMode.NONE, defense_enabled=False).run("baseline")
        attacked = MissionSimulator(ticks, seed, AttackMode.HYBRID, defense_enabled=False).run("attacked")
        refs[seed] = {
            "baseline": baseline.metrics,
            "attacked": attacked.metrics,
        }
    return refs


def generate_candidates(rng: random.Random, count: int) -> list[dict[str, float]]:
    candidates = [
        DEFAULT_CONFIG,
        {
            **DEFAULT_CONFIG,
            "ml_priority_threshold": 0.30,
            "ml_minimum_mode_threshold": 0.58,
            "ml_pace_threshold": 0.43,
            "recovery_stable_ticks_required": 2,
            "satcom_return_health_threshold": 0.84,
            "satcom_return_risk_threshold": 0.48,
        },
        {
            **DEFAULT_CONFIG,
            "ml_weight": 0.74,
            "heuristic_weight": 0.26,
            "ml_priority_threshold": 0.28,
            "ml_minimum_mode_threshold": 0.50,
            "ml_pace_threshold": 0.39,
            "recovery_stable_ticks_required": 2,
            "recovery_queue_threshold": 16,
            "satcom_return_health_threshold": 0.82,
            "satcom_return_risk_threshold": 0.46,
        },
        {
            **DEFAULT_CONFIG,
            "ml_weight": 0.58,
            "heuristic_weight": 0.42,
            "ml_priority_threshold": 0.24,
            "ml_minimum_mode_threshold": 0.46,
            "ml_pace_threshold": 0.36,
            "critical_queue_guard_threshold": 0,
            "queue_guard_threshold": 2,
            "satcom_return_health_threshold": 0.80,
            "satcom_return_risk_threshold": 0.44,
        },
    ]

    while len(candidates) < count:
        ml_weight = round(rng.uniform(0.52, 0.84), 4)
        candidates.append(
            {
                "ml_alert_threshold": round(rng.uniform(0.38, 0.58), 4),
                "ml_priority_threshold": round(rng.uniform(0.18, 0.46), 4),
                "ml_minimum_mode_threshold": round(rng.uniform(0.40, 0.78), 4),
                "ml_pace_threshold": round(rng.uniform(0.32, 0.58), 4),
                "ml_stale_badge_threshold": round(rng.uniform(0.48, 0.74), 4),
                "ml_quarantine_threshold": round(rng.uniform(0.65, 0.86), 4),
                "ml_recovery_threshold": round(rng.uniform(0.22, 0.40), 4),
                "ml_weight": ml_weight,
                "heuristic_weight": round(1.0 - ml_weight, 4),
                "recovery_stable_ticks_required": rng.choice([2, 3, 4]),
                "recovery_queue_threshold": rng.choice([8, 10, 12, 14, 16, 18]),
                "recovery_latency_threshold": rng.choice([5.0, 5.5, 6.0, 6.5, 7.0]),
                "critical_queue_guard_threshold": rng.choice([0, 1, 2]),
                "queue_guard_threshold": rng.choice([1, 2, 3, 4, 5, 6]),
                "satcom_guard_threshold": round(rng.uniform(0.84, 0.98), 4),
                "satcom_return_health_threshold": round(rng.uniform(0.76, 0.90), 4),
                "satcom_return_risk_threshold": round(rng.uniform(0.38, 0.56), 4),
            }
        )
    return candidates


def evaluate_config(
    config: dict[str, float],
    ticks: int,
    refs: dict[int, dict[str, RunMetrics]],
    sklearn_model: object,
) -> dict[str, Any]:
    rows = []
    guarded_rows = []
    for seed, reference in refs.items():
        defended = MissionSimulator(
            ticks,
            seed,
            AttackMode.HYBRID,
            defense_enabled=True,
            defense_mode="ml",
            defense_config=config,
            sklearn_model=sklearn_model,
        ).run("ml_defended")
        guarded = MissionSimulator(
            ticks,
            seed,
            AttackMode.NONE,
            defense_enabled=True,
            defense_mode="ml",
            defense_config=config,
            sklearn_model=sklearn_model,
        ).run("ml_guarded_baseline")
        rows.append(
            {
                "seed": seed,
                "metrics": defended.metrics,
                "gain": resilience_gain(reference["attacked"], defended.metrics, reference["baseline"]),
            }
        )
        guarded_rows.append({"seed": seed, "metrics": guarded.metrics})

    metrics = summarize_rows(rows, guarded_rows)
    objective = objective_score(metrics)
    return {"objective": objective, "metrics": metrics}


def summarize_rows(rows: list[dict[str, Any]], guarded_rows: list[dict[str, Any]]) -> dict[str, Any]:
    defended = [row["metrics"] for row in rows]
    guarded = [row["metrics"] for row in guarded_rows]
    return {
        "mission_impact_score": round(mean(metric.mission_impact_score for metric in defended), 4),
        "p95_critical_latency": round(mean(metric.p95_critical_latency for metric in defended), 4),
        "stale_data_ratio": round(mean(metric.stale_data_ratio for metric in defended), 4),
        "priority_inversion_rate": round(mean(metric.priority_inversion_rate for metric in defended), 4),
        "deferred_messages": round(mean(metric.deferred_messages for metric in defended), 4),
        "shed_messages": round(mean(metric.shed_messages for metric in defended), 4),
        "compressed_messages": round(mean(metric.compressed_messages for metric in defended), 4),
        "backlog_messages": round(mean(metric.backlog_messages for metric in defended), 4),
        "expired_messages": round(mean(metric.expired_messages for metric in defended), 4),
        "detection_time": average_nullable([metric.detection_time for metric in defended]),
        "recovery_time": average_nullable([metric.recovery_time for metric in defended]),
        "missing_detection_count": sum(1 for metric in defended if metric.detection_time is None),
        "missing_recovery_count": sum(1 for metric in defended if metric.recovery_time is None),
        "false_alarm_rate": round(mean(metric.false_alarm_rate for metric in guarded), 4),
        "false_alarm_count": round(mean(metric.false_alarm_count for metric in guarded), 4),
        "resilience_gain_percent": round(mean(row["gain"] for row in rows), 4),
        "defense_intervention_ticks": round(
            mean(metric.defense_intervention_ticks for metric in defended),
            4,
        ),
        "priority_boost_ticks": round(
            mean(metric.priority_boost_ticks for metric in defended),
            4,
        ),
        "model_influenced_ticks": round(
            mean(metric.model_influenced_ticks for metric in defended),
            4,
        ),
        "model_influenced_action_count": round(
            mean(metric.model_influenced_action_count for metric in defended),
            4,
        ),
        "minimum_model_influenced_ticks": min(
            metric.model_influenced_ticks for metric in defended
        ),
        "missing_model_influence_seed_count": sum(
            metric.model_influenced_ticks == 0 for metric in defended
        ),
        "guarded_intervention_ticks": round(
            mean(metric.defense_intervention_ticks for metric in guarded),
            4,
        ),
        "guarded_model_influenced_ticks": round(
            mean(metric.model_influenced_ticks for metric in guarded),
            4,
        ),
    }


def average_nullable(values: list[int | None]) -> float | None:
    numeric = [value for value in values if value is not None]
    if not numeric:
        return None
    return round(mean(numeric), 4)


def objective_score(metrics: dict[str, Any]) -> float:
    missing_detection = float(metrics["missing_detection_count"])
    missing_recovery = float(metrics["missing_recovery_count"])
    detection_time = metrics["detection_time"] if metrics["detection_time"] is not None else 12.0
    recovery_time = metrics["recovery_time"] if metrics["recovery_time"] is not None else 10.0
    excessive_deferral = max(0.0, float(metrics["deferred_messages"]) - 52.0)
    excessive_compression = max(0.0, float(metrics["compressed_messages"]) - 70.0)
    excessive_shedding = max(0.0, float(metrics["shed_messages"]) - 28.0)
    missing_model_influence = float(metrics["missing_model_influence_seed_count"])
    return round(
        float(metrics["mission_impact_score"])
        + float(metrics["priority_inversion_rate"]) * 260.0
        + float(metrics["stale_data_ratio"]) * 28.0
        + float(metrics["false_alarm_rate"]) * 500.0
        + missing_detection * 12.0
        + missing_recovery * 8.0
        + detection_time * 0.35
        + recovery_time * 0.25
        + excessive_deferral * 0.10
        + excessive_compression * 0.04
        + excessive_shedding * 0.08
        + float(metrics["defense_intervention_ticks"]) * 0.003
        + float(metrics["priority_boost_ticks"]) * 0.002
        + float(metrics["guarded_intervention_ticks"]) * 0.004
        + missing_model_influence * 8.0
        + float(metrics["guarded_model_influenced_ticks"]) * 0.20,
        4,
    )


if __name__ == "__main__":
    main()
