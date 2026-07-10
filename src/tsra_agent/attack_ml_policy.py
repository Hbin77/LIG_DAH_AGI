from __future__ import annotations

import hashlib
import hmac
import io
import json
from pathlib import Path
from typing import Any, Protocol

from .agents import MissionState
from .models import AttackMode, LinkName


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ATTACK_MODEL_PATH = ROOT / "models" / "aura_rollout_policy.joblib"
DEFAULT_ATTACK_CONFIG_PATH = ROOT / "models" / "aura_ml_policy_config.json"
AURA_ML_SCENARIO = AttackMode.HYBRID
AURA_ML_TICKS = 180
ATTACK_FEATURE_SCHEMA_VERSION = "aura-attack-features/v2"

ATTACK_FEATURE_NAMES = [
    "tick_progress",
    "satcom_degradation",
    "radio_health",
    "lte_health",
    "mesh_health",
    "queue_pressure",
    "critical_queue_pressure",
    "stale_ratio",
    "critical_latency_pressure",
    "priority_inversion_pressure",
    "terminal_risk",
    "source_trust_drop",
    "pace_instability",
    "active_link_satcom",
    "active_link_radio",
    "active_link_lte",
    "active_link_mesh",
    "action_none",
    "action_link_degradation",
    "action_mission_aware_delay",
    "action_failover_chasing",
    "target_link_satcom",
    "target_link_radio",
    "target_link_lte",
    "target_link_mesh",
    "intensity",
    "duration_pressure",
]


class AttackImpactModel(Protocol):
    def predict(self, rows: list[list[float]]) -> Any: ...


class AblatedAttackImpactModel:
    """Removes learned impact while preserving the AURA-ML decision path."""

    def predict(self, rows: list[list[float]]) -> list[float]:
        return [0.0 for _ in rows]


def attack_candidate_features(
    state: MissionState,
    candidate: dict[str, Any],
) -> list[float]:
    action = AttackMode(str(candidate["action"]))
    target = LinkName(str(candidate["target_link"]))
    active_link = state.active_link
    return [
        clamp(state.tick / float(AURA_ML_TICKS)),
        clamp(1.0 - state.satcom_health),
        clamp(state.radio_health),
        clamp(state.lte_health),
        clamp(state.mesh_health),
        clamp(state.queue_depth / 80.0),
        clamp(state.critical_queue_depth / 20.0),
        clamp(state.stale_ratio_window),
        clamp(state.critical_latency_window / 14.0),
        clamp(state.priority_inversion_window / 0.25),
        clamp(state.terminal_risk_window),
        clamp(state.source_trust_drop_window),
        clamp(state.pace_instability_window),
        float(active_link == LinkName.SATCOM),
        float(active_link == LinkName.RADIO),
        float(active_link == LinkName.LTE),
        float(active_link == LinkName.MESH),
        float(action == AttackMode.NONE),
        float(action == AttackMode.LINK_DEGRADATION),
        float(action == AttackMode.MISSION_AWARE_DELAY),
        float(action == AttackMode.FAILOVER_CHASING),
        float(target == LinkName.SATCOM),
        float(target == LinkName.RADIO),
        float(target == LinkName.LTE),
        float(target == LinkName.MESH),
        clamp(float(candidate["intensity"])),
        clamp(float(candidate["duration"]) / 30.0),
    ]


def load_attack_model(
    path: Path = DEFAULT_ATTACK_MODEL_PATH,
    *,
    expected_sha256: str | None = None,
    config_path: Path = DEFAULT_ATTACK_CONFIG_PATH,
) -> AttackImpactModel:
    from joblib import load

    payload = path.read_bytes()
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    if expected_sha256 is None:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        expected_sha256 = str(config["model_sha256"])
    if not hmac.compare_digest(actual_sha256, expected_sha256):
        raise ValueError(
            f"AURA model SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )
    model = load(io.BytesIO(payload))
    if getattr(model, "n_features_in_", None) != len(ATTACK_FEATURE_NAMES):
        raise ValueError("AURA model feature contract mismatch")
    return model


def load_attack_policy_config(path: Path = DEFAULT_ATTACK_CONFIG_PATH) -> dict[str, float]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    config = payload.get("config", payload)
    return {key: float(value) for key, value in config.items()}


def attack_model_backend_name(model: object) -> str:
    class_name = type(model).__name__
    if class_name == "HistGradientBoostingRegressor":
        return "sklearn_hist_gradient_boosting_regressor"
    if class_name == "ExtraTreesRegressor":
        return "sklearn_extra_trees_regressor"
    if class_name == "RandomForestRegressor":
        return "sklearn_random_forest_regressor"
    if class_name == "AblatedAttackImpactModel":
        return "ablation_zero_impact_model"
    return f"sklearn_{class_name.lower()}"


def validate_attack_ml_scope(scenario: AttackMode, ticks: int) -> None:
    if scenario != AURA_ML_SCENARIO or ticks != AURA_ML_TICKS:
        raise ValueError(
            "AURA-ML is validated only for scenario=hybrid and ticks=180; "
            f"received scenario={scenario.value}, ticks={ticks}"
        )


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(upper, max(lower, value))
