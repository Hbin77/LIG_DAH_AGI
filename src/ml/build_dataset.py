from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

from src.aura.candidate_generator import generate_candidates
from src.aura.impact_estimator import estimate_candidate_effect
from src.shared.features import candidate_features
from src.shared.schemas import LinkState, MissionState


def random_state(rng: random.Random, sample_id: int) -> MissionState:
    phase = rng.choice(["normal_patrol", "air_defense_watch", "resupply_move"])
    active_link = rng.choice(["SATCOM", "SATCOM", "SATCOM", "LTE", "TACTICAL_RADIO"])
    links = {
        "SATCOM": LinkState(
            "SATCOM",
            True,
            rng.uniform(1.0, 6.0),
            rng.uniform(500, 1500),
            rng.uniform(40, 250),
            rng.uniform(0.005, 0.08),
            rng.randint(0, 80),
        ),
        "TACTICAL_RADIO": LinkState(
            "TACTICAL_RADIO",
            True,
            rng.uniform(0.4, 1.2),
            rng.uniform(180, 500),
            rng.uniform(30, 120),
            rng.uniform(0.01, 0.08),
            rng.randint(0, 35),
        ),
        "LTE": LinkState(
            "LTE",
            True,
            rng.uniform(1.2, 5.0),
            rng.uniform(80, 350),
            rng.uniform(20, 100),
            rng.uniform(0.005, 0.06),
            rng.randint(0, 50),
        ),
        "MESH": LinkState(
            "MESH",
            True,
            rng.uniform(0.6, 2.0),
            rng.uniform(120, 450),
            rng.uniform(30, 140),
            rng.uniform(0.01, 0.07),
            rng.randint(0, 40),
        ),
    }
    queue_kb_by_type = {
        "video": rng.uniform(0, 6000),
        "telemetry": rng.uniform(0, 500),
        "air_defense_alert": rng.uniform(0, 80) if phase == "air_defense_watch" else rng.uniform(0, 20),
        "command": rng.uniform(0, 80),
        "coordinate": rng.uniform(0, 100),
    }
    queue_count_by_type = {
        key: max(0, int(value / 40)) for key, value in queue_kb_by_type.items()
    }
    critical_pending = (
        queue_count_by_type.get("air_defense_alert", 0)
        + queue_count_by_type.get("command", 0)
        + queue_count_by_type.get("coordinate", 0)
    )
    return MissionState(
        time_sec=float(sample_id % 300),
        mission_phase=phase,
        active_link=active_link,
        links=links,
        queue_count_by_type=queue_count_by_type,
        queue_kb_by_type=queue_kb_by_type,
        total_queue_kb=sum(queue_kb_by_type.values()),
        critical_pending=critical_pending,
        video_queue_kb=queue_kb_by_type["video"],
        stale_data_ratio=rng.uniform(0.0, 0.7),
        recent_p95_critical_latency_sec=rng.uniform(0.0, 55.0),
        priority_inversion_rate=rng.uniform(0.0, 0.45),
        defense_mode=rng.choice(["none", "none", "tsra_r", "pace_switch"]),
    )


def build_dataset(rows: int, output: Path, seed: int) -> None:
    rng = random.Random(seed)
    output.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for sample_id in range(rows):
        state = random_state(rng, sample_id)
        for candidate_id, candidate in enumerate(generate_candidates(state)):
            features = candidate_features(state, candidate)
            label = estimate_candidate_effect(state, candidate)["mission_impact"]
            record = {
                "sample_id": sample_id,
                "candidate_id": candidate_id,
                "attack_type": candidate.attack_type,
                "label_mission_impact": label,
            }
            record.update(features)
            records.append(record)

    fieldnames = sorted({key for record in records for key in record})
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} rows to {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("outputs/datasets/aura_candidate_dataset.csv"))
    args = parser.parse_args()
    build_dataset(args.rows, args.output, args.seed)


if __name__ == "__main__":
    main()

