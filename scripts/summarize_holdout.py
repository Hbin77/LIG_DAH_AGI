from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEVELOPMENT_SEEDS = {7, 11, 19, 23, 31, 41, 43, 47, 53, 59}
CONDITIONS = [
    "baseline",
    "attacked",
    "rule_defended",
    "defended",
    "ml_defended",
    "ml_ablated",
    "guarded_baseline",
    "ml_guarded_baseline",
]
METRICS = [
    "mission_impact_score",
    "p95_critical_latency",
    "stale_data_ratio",
    "priority_inversion_rate",
    "false_alarm_rate",
    "defense_intervention_ticks",
    "priority_boost_ticks",
    "model_influenced_ticks",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a compact post-tuning holdout summary.")
    parser.add_argument("--input", required=True, help="Full CLI summary.json from the holdout run.")
    parser.add_argument("--output", default="examples/holdout_30_seed_summary.json")
    parser.add_argument("--expected-seeds", type=int, default=30)
    parser.add_argument("--bootstrap-samples", type=int, default=20000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    source_bytes = input_path.read_bytes()
    summary = json.loads(source_bytes)
    seeds = [int(seed) for seed in summary["seeds"]]
    if len(seeds) != args.expected_seeds or len(set(seeds)) != args.expected_seeds:
        raise ValueError(
            f"expected {args.expected_seeds} unique seeds, got {len(seeds)} rows and {len(set(seeds))} unique"
        )
    overlap = sorted(set(seeds) & DEFAULT_DEVELOPMENT_SEEDS)
    if overlap:
        raise ValueError(f"holdout seeds overlap model/tuning development seeds: {overlap}")
    if set(CONDITIONS) - set(summary["aggregate"]):
        raise ValueError("holdout summary is missing required experiment conditions")

    compact = {
        "schema_version": "tsra-post-tuning-holdout/v1",
        "evaluation_kind": "post_tuning_holdout",
        "scenario": summary["scenario"],
        "ticks": summary["ticks"],
        "seeds": seeds,
        "seed_count": len(seeds),
        "development_seed_exclusion": sorted(DEFAULT_DEVELOPMENT_SEEDS),
        "source_summary_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "model_sha256": sha256(ROOT / "models/tsra_sklearn_policy.joblib"),
        "policy_config_sha256": sha256(ROOT / "models/tsra_ml_policy_config.json"),
        "aggregate": {
            condition: {
                metric: summary["aggregate"][condition][metric]
                for metric in METRICS
            }
            for condition in CONDITIONS
        },
        "resilience_gain_percent": {
            key: summary["aggregate"][key]
            for key in [
                "rule_resilience_gain_percent",
                "resilience_gain_percent",
                "ml_resilience_gain_percent",
                "ml_ablated_resilience_gain_percent",
            ]
        },
        "paired_mission_impact": {
            "tsra_r_minus_tsra_ml": paired_difference(
                summary["runs"],
                "defended",
                "ml_defended",
                args.bootstrap_samples,
                seed=20260710,
            ),
            "zero_model_ablation_minus_tsra_ml": paired_difference(
                summary["runs"],
                "ml_ablated",
                "ml_defended",
                args.bootstrap_samples,
                seed=20260711,
            ),
        },
        "limitations": [
            "Holdout seeds vary simulator stochastic loss and delivery outcomes, not real operational environments.",
            "The model wins on average but not on every seed; win/loss counts are reported explicitly.",
            "Bootstrap intervals quantify simulator-seed uncertainty only.",
        ],
        "safety_boundary": {
            "synthetic_mission_event_simulator_only": True,
            "exploit_code": False,
            "operational_rf_parameters": False,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(compact, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(output_path)


def paired_difference(
    runs: list[dict[str, Any]],
    left: str,
    right: str,
    bootstrap_samples: int,
    *,
    seed: int,
) -> dict[str, Any]:
    differences = [
        float(run[left]["mission_impact_score"])
        - float(run[right]["mission_impact_score"])
        for run in runs
    ]
    rng = random.Random(seed)
    bootstrap_means = sorted(
        mean(rng.choice(differences) for _ in differences)
        for _ in range(bootstrap_samples)
    )
    lower_index = int(0.025 * (bootstrap_samples - 1))
    upper_index = int(0.975 * (bootstrap_samples - 1))
    return {
        "meaning": f"positive values favor {right}",
        "count": len(differences),
        "mean": round(mean(differences), 4),
        "stdev": round(pstdev(differences), 4),
        "bootstrap_95_percent_ci": [
            round(bootstrap_means[lower_index], 4),
            round(bootstrap_means[upper_index], 4),
        ],
        "wins": sum(value > 0 for value in differences),
        "ties": sum(value == 0 for value in differences),
        "losses": sum(value < 0 for value in differences),
        "min": round(min(differences), 4),
        "max": round(max(differences), 4),
        "bootstrap_samples": bootstrap_samples,
        "bootstrap_seed": seed,
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    main()
