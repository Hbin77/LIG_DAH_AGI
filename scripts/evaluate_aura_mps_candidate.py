from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tsra_agent.attack_ml_policy import (
    DEFAULT_ATTACK_MODEL_PATH,
    DEFAULT_MPS_STUDENT_PATH,
    load_attack_model,
    load_mps_student_model,
)
from src.tsra_agent.ml_policy import load_sklearn_model
from src.tsra_agent.models import AttackMode
from src.tsra_agent.simulator import MissionSimulator


DEFAULT_SEEDS = "1103,1109,1117,1123,1129,1151,1153,1163,1171,1181"
DEFAULT_CONTEXTS = "none,rule,tsra,ml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the closed-loop promotion gate for the MPS-trained AURA student."
    )
    parser.add_argument("--seeds", default=DEFAULT_SEEDS)
    parser.add_argument("--contexts", default=DEFAULT_CONTEXTS)
    parser.add_argument("--ticks", type=int, default=180)
    parser.add_argument(
        "--output",
        default="models/aura_mps_selection_report.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seeds = parse_ints(args.seeds)
    contexts = parse_strings(args.contexts)
    tree_model = load_attack_model()
    mps_model = load_mps_student_model()
    defense_model = load_sklearn_model() if "ml" in contexts else None
    results: dict[str, Any] = {}

    for context in contexts:
        rows = []
        tree_actions: Counter[str] = Counter()
        mps_actions: Counter[str] = Counter()
        for seed in seeds:
            defense_enabled = context != "none"
            defense_mode = "tsra" if context == "none" else context
            common = {
                "ticks": args.ticks,
                "seed": seed,
                "attack_mode": AttackMode.HYBRID,
                "defense_enabled": defense_enabled,
                "defense_mode": defense_mode,
                "sklearn_model": defense_model if context == "ml" else None,
                "attack_policy": "ml",
                "retain_agent_traces": False,
            }
            tree_simulator = MissionSimulator(**common, attack_model=tree_model)
            tree_result = tree_simulator.run("aura_extra_trees")
            mps_simulator = MissionSimulator(**common, attack_model=mps_model)
            mps_result = mps_simulator.run("aura_mps_student")
            tree_actions.update(tree_simulator.red.action_counts)
            mps_actions.update(mps_simulator.red.action_counts)
            rows.append(
                {
                    "seed": seed,
                    "extra_trees_impact": tree_result.metrics.mission_impact_score,
                    "mps_impact": mps_result.metrics.mission_impact_score,
                    "mps_minus_extra_trees": round(
                        mps_result.metrics.mission_impact_score
                        - tree_result.metrics.mission_impact_score,
                        4,
                    ),
                }
            )
        differences = [row["mps_minus_extra_trees"] for row in rows]
        results[context] = {
            "extra_trees_impact_mean": round(
                mean(row["extra_trees_impact"] for row in rows),
                4,
            ),
            "mps_impact_mean": round(mean(row["mps_impact"] for row in rows), 4),
            "paired_mps_minus_extra_trees": {
                "mean": round(mean(differences), 4),
                "stdev": round(pstdev(differences), 4),
                "wins": sum(value > 0.0 for value in differences),
                "ties": sum(value == 0.0 for value in differences),
                "losses": sum(value < 0.0 for value in differences),
                "count": len(differences),
                "minimum": round(min(differences), 4),
                "maximum": round(max(differences), 4),
            },
            "extra_trees_action_counts": dict(sorted(tree_actions.items())),
            "mps_action_counts": dict(sorted(mps_actions.items())),
            "runs": rows,
        }
        print(
            f"{context}: mps-tree={results[context]['paired_mps_minus_extra_trees']['mean']}",
            flush=True,
        )

    all_context_noninferior = all(
        result["paired_mps_minus_extra_trees"]["mean"] >= 0.0
        for result in results.values()
    )
    defended_context_noninferior = all(
        results[context]["paired_mps_minus_extra_trees"]["mean"] >= 0.0
        for context in contexts
        if context != "none"
    )
    mps_metrics = read_json(ROOT / "models/aura_mps_student_metrics.json")
    payload = {
        "schema_version": "aura-mps-selection/v1",
        "seeds": seeds,
        "seed_count": len(seeds),
        "contexts": contexts,
        "ticks": args.ticks,
        "model_provenance": {
            "extra_trees_path": display_path(DEFAULT_ATTACK_MODEL_PATH),
            "extra_trees_sha256": sha256(DEFAULT_ATTACK_MODEL_PATH),
            "mps_checkpoint_sha256": mps_metrics["model_sha256"],
            "mps_portable_path": display_path(DEFAULT_MPS_STUDENT_PATH),
            "mps_portable_sha256": sha256(DEFAULT_MPS_STUDENT_PATH),
        },
        "candidate_validation": {
            "mps": mps_metrics["validation"],
            "extra_trees": mps_metrics["primary_extra_trees_comparison"],
        },
        "closed_loop_development_gate": results,
        "promotion_decision": {
            "candidate_validation_pass": mps_metrics["promotion_decision"][
                "candidate_for_closed_loop_promotion"
            ],
            "all_context_noninferior": all_context_noninferior,
            "defended_context_noninferior": defended_context_noninferior,
            "promote_to_agent_runtime": (
                all_context_noninferior and defended_context_noninferior
            ),
            "selected_runtime_backend": (
                "mps_trained_numpy_mlp"
                if all_context_noninferior and defended_context_noninferior
                else "sklearn_extra_trees_regressor"
            ),
            "reason": (
                "MPS student failed at least one closed-loop context; validation ranking "
                "improvement alone is insufficient for runtime promotion."
                if not all_context_noninferior
                else "MPS student passed the development promotion gate."
            ),
        },
        "holdout_policy": (
            "No new 30-seed promotion holdout was consumed because the MPS student failed "
            "the predeclared development gate."
        ),
        "safety_boundary": {
            "synthetic_mission_effects_only": True,
            "exploit_code": False,
            "operational_rf_parameters": False,
            "live_network_actions": False,
        },
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(payload["promotion_decision"], indent=2))
    print(f"output: {output_path}")


def parse_ints(value: str) -> list[int]:
    parsed = [int(part.strip()) for part in value.split(",") if part.strip()]
    if not parsed:
        raise ValueError("seed list must not be empty")
    return parsed


def parse_strings(value: str) -> list[str]:
    parsed = [part.strip() for part in value.split(",") if part.strip()]
    if not parsed:
        raise ValueError("context list must not be empty")
    return parsed


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
