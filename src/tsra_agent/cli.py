from __future__ import annotations

import argparse
import json
from statistics import mean, pstdev
from datetime import datetime
from pathlib import Path
from typing import Any

from .evaluator import resilience_gain
from .models import AttackMode
from .simulator import MissionSimulator, write_result


EXPERIMENTS = {
    "baseline": "E1 no attack, default mission routing baseline",
    "attacked": "E2 hybrid AURA-lite mission-effect attack without defense",
    "rule_defended": "E3 threshold rule defense against the same attack",
    "defended": "E4/E5 TSRA-R risk-fusion defense against the same attack",
    "ml_defended": "E6 TSRA-ML trained ensemble and tuned action-gate defense against the same attack",
    "guarded_baseline": "False-alarm check: TSRA-R monitoring under no attack",
    "ml_guarded_baseline": "False-alarm check: TSRA-ML monitoring under no attack",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run TSRA-R / AURA-lite mission simulation.")
    parser.add_argument("--scenario", default="hybrid", choices=[mode.value for mode in AttackMode])
    parser.add_argument("--ticks", type=int, default=180)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--seeds", default=None, help="Comma-separated seeds. Overrides --seed when provided.")
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else Path("outputs") / f"run_{datetime.now():%Y%m%d_%H%M%S}"
    scenario = AttackMode(args.scenario)
    seeds = parse_seeds(args.seeds, args.seed)

    summary = run_suite(scenario, args.ticks, seeds, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "incident_report.md").write_text(build_report(summary), encoding="utf-8")
    (output_dir / "run_manifest.json").write_text(
        json.dumps(build_manifest(summary), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\noutputs: {output_dir}")


def parse_seeds(seed_arg: str | None, fallback_seed: int) -> list[int]:
    if not seed_arg:
        return [fallback_seed]
    seeds = [int(part.strip()) for part in seed_arg.split(",") if part.strip()]
    if not seeds:
        raise ValueError("--seeds must contain at least one integer seed")
    return seeds


def run_suite(scenario: AttackMode, ticks: int, seeds: list[int], output_dir: Path) -> dict[str, Any]:
    runs = []
    for seed in seeds:
        seed_dir = output_dir / f"seed_{seed}" if len(seeds) > 1 else output_dir
        baseline = MissionSimulator(ticks, seed, AttackMode.NONE, defense_enabled=False).run("baseline")
        attacked = MissionSimulator(ticks, seed, scenario, defense_enabled=False).run("attacked")
        rule_defended = MissionSimulator(
            ticks,
            seed,
            scenario,
            defense_enabled=True,
            defense_mode="rule",
        ).run("rule_defended")
        defended = MissionSimulator(
            ticks,
            seed,
            scenario,
            defense_enabled=True,
            defense_mode="tsra",
        ).run("defended")
        ml_defended = MissionSimulator(
            ticks,
            seed,
            scenario,
            defense_enabled=True,
            defense_mode="ml",
        ).run("ml_defended")
        guarded_baseline = MissionSimulator(
            ticks,
            seed,
            AttackMode.NONE,
            defense_enabled=True,
            defense_mode="tsra",
        ).run("guarded_baseline")
        ml_guarded_baseline = MissionSimulator(
            ticks,
            seed,
            AttackMode.NONE,
            defense_enabled=True,
            defense_mode="ml",
        ).run("ml_guarded_baseline")
        for result in (
            baseline,
            attacked,
            rule_defended,
            defended,
            ml_defended,
            guarded_baseline,
            ml_guarded_baseline,
        ):
            write_result(result, seed_dir)

        run_summary = {
            "seed": seed,
            "baseline": baseline.metrics.as_dict(),
            "attacked": attacked.metrics.as_dict(),
            "rule_defended": rule_defended.metrics.as_dict(),
            "defended": defended.metrics.as_dict(),
            "ml_defended": ml_defended.metrics.as_dict(),
            "guarded_baseline": guarded_baseline.metrics.as_dict(),
            "ml_guarded_baseline": ml_guarded_baseline.metrics.as_dict(),
            "rule_resilience_gain_percent": resilience_gain(attacked.metrics, rule_defended.metrics, baseline.metrics),
            "resilience_gain_percent": resilience_gain(attacked.metrics, defended.metrics, baseline.metrics),
            "ml_resilience_gain_percent": resilience_gain(attacked.metrics, ml_defended.metrics, baseline.metrics),
        }
        runs.append(run_summary)
        (seed_dir / "summary.json").write_text(json.dumps(run_summary, indent=2, ensure_ascii=False), encoding="utf-8")

    summary: dict[str, Any] = {
        "scenario": scenario.value,
        "ticks": ticks,
        "seeds": seeds,
        "experiments": EXPERIMENTS,
        "runs": runs,
        "aggregate": aggregate_runs(runs),
    }
    if len(runs) == 1:
        summary.update(
            {
                "seed": runs[0]["seed"],
                "baseline": runs[0]["baseline"],
                "attacked": runs[0]["attacked"],
                "rule_defended": runs[0]["rule_defended"],
                "defended": runs[0]["defended"],
                "ml_defended": runs[0]["ml_defended"],
                "guarded_baseline": runs[0]["guarded_baseline"],
                "ml_guarded_baseline": runs[0]["ml_guarded_baseline"],
                "rule_resilience_gain_percent": runs[0]["rule_resilience_gain_percent"],
                "resilience_gain_percent": runs[0]["resilience_gain_percent"],
                "ml_resilience_gain_percent": runs[0]["ml_resilience_gain_percent"],
            }
        )
    return summary


def aggregate_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = {
        "baseline": aggregate_metric_dicts([run["baseline"] for run in runs]),
        "attacked": aggregate_metric_dicts([run["attacked"] for run in runs]),
        "rule_defended": aggregate_metric_dicts([run["rule_defended"] for run in runs]),
        "defended": aggregate_metric_dicts([run["defended"] for run in runs]),
        "ml_defended": aggregate_metric_dicts([run["ml_defended"] for run in runs]),
        "guarded_baseline": aggregate_metric_dicts([run["guarded_baseline"] for run in runs]),
        "ml_guarded_baseline": aggregate_metric_dicts([run["ml_guarded_baseline"] for run in runs]),
        "rule_resilience_gain_percent": aggregate_values([run["rule_resilience_gain_percent"] for run in runs]),
        "resilience_gain_percent": aggregate_values([run["resilience_gain_percent"] for run in runs]),
        "ml_resilience_gain_percent": aggregate_values([run["ml_resilience_gain_percent"] for run in runs]),
    }
    return aggregate


def aggregate_metric_dicts(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    keys = metrics[0].keys()
    return {key: aggregate_values([metric[key] for metric in metrics]) for key in keys}


def aggregate_values(values: list[Any]) -> dict[str, Any]:
    numeric = [value for value in values if isinstance(value, (int, float))]
    if not numeric:
        return {"mean": None, "stdev": None, "count": 0}
    return {
        "mean": round(mean(numeric), 4),
        "stdev": round(pstdev(numeric), 4) if len(numeric) > 1 else 0.0,
        "count": len(numeric),
    }


def build_manifest(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "tsra-run-manifest/v1",
        "scenario": summary["scenario"],
        "ticks": summary["ticks"],
        "seeds": summary["seeds"],
        "experiments": summary["experiments"],
        "artifacts": [
            "summary.json",
            "incident_report.md",
            "run_manifest.json",
            "models/tsra_ml_policy.json",
            "models/tsra_ml_training_report.json",
            "models/tsra_sklearn_policy.joblib",
            "models/tsra_sklearn_training_report.json",
            "models/tsra_ml_policy_config.json",
            "models/tsra_ml_tuning_report.json",
            "models/tsra_final_selection_report.json",
            "seed_<seed>/<experiment>_events.jsonl",
            "seed_<seed>/summary.json",
        ],
        "safety_boundary": {
            "exploit_code": False,
            "operational_rf_parameters": False,
            "equipment_specific_intrusion_steps": False,
            "synthetic_mission_event_simulator_only": True,
        },
    }


def build_report(summary: dict) -> str:
    attacked = summary["aggregate"]["attacked"]
    rule_defended = summary["aggregate"]["rule_defended"]
    defended = summary["aggregate"]["defended"]
    ml_defended = summary["aggregate"]["ml_defended"]
    guarded = summary["aggregate"]["guarded_baseline"]
    ml_guarded = summary["aggregate"]["ml_guarded_baseline"]
    gain = summary["aggregate"]["resilience_gain_percent"]
    ml_gain = summary["aggregate"]["ml_resilience_gain_percent"]
    rule_gain = summary["aggregate"]["rule_resilience_gain_percent"]
    return f"""# TSRA-R / AURA-lite Incident Summary

## Scenario

- Mode: `{summary["scenario"]}`
- Ticks: `{summary["ticks"]}`
- Seeds: `{", ".join(str(seed) for seed in summary["seeds"])}`

## Key Findings

- AURA-lite increased mean mission impact score to `{attacked["mission_impact_score"]["mean"]}` under the attack condition.
- Rule defense reduced mean mission impact score to `{rule_defended["mission_impact_score"]["mean"]}` with `{rule_gain["mean"]}%` baseline-adjusted gain.
- TSRA-R-lite reduced mean mission impact score to `{defended["mission_impact_score"]["mean"]}`.
- Mean baseline-adjusted resilience gain was `{gain["mean"]}%`.
- TSRA-ML reduced mean mission impact score to `{ml_defended["mission_impact_score"]["mean"]}`.
- TSRA-ML mean baseline-adjusted resilience gain was `{ml_gain["mean"]}%`.
- Defended mean P95 critical latency: `{defended["p95_critical_latency"]["mean"]}` ticks.
- Defended mean stale data ratio: `{defended["stale_data_ratio"]["mean"]}`.
- Defended mean priority inversion rate: `{defended["priority_inversion_rate"]["mean"]}`.
- TSRA-ML mean P95 critical latency: `{ml_defended["p95_critical_latency"]["mean"]}` ticks.
- TSRA-ML mean stale data ratio: `{ml_defended["stale_data_ratio"]["mean"]}`.
- TSRA-ML mean priority inversion rate: `{ml_defended["priority_inversion_rate"]["mean"]}`.
- TSRA-ML mean compressed snapshot messages: `{ml_defended["compressed_messages"]["mean"]}`.
- TSRA-ML mean deferred messages: `{ml_defended["deferred_messages"]["mean"]}`.
- TSRA-ML mean backlog messages: `{ml_defended["backlog_messages"]["mean"]}`.
- TSRA-ML mean expired messages: `{ml_defended["expired_messages"]["mean"]}`.
- TSRA-R mean detection time: `{defended["detection_time"]["mean"]}` ticks after first attack.
- TSRA-R mean recovery time: `{defended["recovery_time"]["mean"]}` ticks after first TSRA-R alert stabilization.
- Guarded no-attack false alarm rate: `{guarded["false_alarm_rate"]["mean"]}`.
- TSRA-ML guarded no-attack false alarm rate: `{ml_guarded["false_alarm_rate"]["mean"]}`.

## Agent Actions

- AURA-lite selected bounded, abstract COAs across link degradation, mission-aware delay, and failover chasing inside a synthetic mission-event simulator.
- TSRA-R-lite applied risk fusion, critical traffic priority boosting, PACE routing, COP stale badge, terminal/source quarantine flags, and minimum mode.
- TSRA-ML used a trained scikit-learn ensemble plus tuned guardrail policy for earlier priority boosting, adaptive UAV snapshot compression, EDF scheduling, SATCOM return hysteresis, and stale noncritical backlog control.

## Safety Boundary

The run models mission effects only. It does not include exploit code, equipment-specific procedures, or operational RF parameters.
"""


if __name__ == "__main__":
    main()
