from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from .agents import MissionState
from .models import AttackMode, LinkName


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ATTACK_MODEL_PATH = ROOT / "models" / "aura_rollout_policy.joblib"
DEFAULT_ATTACK_CONFIG_PATH = ROOT / "models" / "aura_ml_policy_config.json"
DEFAULT_MPS_STUDENT_PATH = ROOT / "models" / "aura_mps_student_weights.npz"

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
    "defense_alerted",
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


class NumpyMLPImpactModel:
    """Portable CPU inference for the MLP trained on Apple MPS."""

    def __init__(self, weights: dict[str, Any]) -> None:
        self.weights = weights
        self.n_features_in_ = int(weights["input_dim"])
        self.label_mean = float(weights["label_mean"])
        self.label_scale = float(weights["label_scale"])

    def predict(self, rows: list[list[float]]) -> Any:
        import numpy
        from scipy.special import ndtr

        values = numpy.asarray(rows, dtype=numpy.float32)
        values = self._linear(values, "network.0")
        values = values * ndtr(values)
        mean = values.mean(axis=-1, keepdims=True)
        variance = values.var(axis=-1, keepdims=True)
        values = (values - mean) / numpy.sqrt(variance + 1e-5)
        values = (
            values * self.weights["network.2.weight"]
            + self.weights["network.2.bias"]
        )
        values = self._linear(values, "network.4")
        values = values * ndtr(values)
        values = self._linear(values, "network.7")
        values = values * ndtr(values)
        values = self._linear(values, "network.9").reshape(-1)
        return values * self.label_scale + self.label_mean

    def _linear(self, values: Any, prefix: str) -> Any:
        return values @ self.weights[f"{prefix}.weight"].T + self.weights[f"{prefix}.bias"]


def attack_candidate_features(
    state: MissionState,
    candidate: dict[str, Any],
    *,
    expected_ticks: int = 180,
) -> list[float]:
    action = AttackMode(str(candidate["action"]))
    target = LinkName(str(candidate["target_link"]))
    active_link = state.active_link
    return [
        clamp(state.tick / max(1.0, float(expected_ticks))),
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
        float(state.defense_alerted),
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


def load_attack_model(path: Path = DEFAULT_ATTACK_MODEL_PATH) -> AttackImpactModel:
    from joblib import load

    return load(path)


def load_mps_student_model(
    path: Path = DEFAULT_MPS_STUDENT_PATH,
) -> NumpyMLPImpactModel:
    import numpy

    with numpy.load(path, allow_pickle=False) as payload:
        weights = {key: payload[key].copy() for key in payload.files}
    model = NumpyMLPImpactModel(weights)
    if model.n_features_in_ != len(ATTACK_FEATURE_NAMES):
        raise ValueError("MPS student feature contract mismatch")
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
    if class_name == "NumpyMLPImpactModel":
        return "mps_trained_numpy_mlp"
    return f"sklearn_{class_name.lower()}"


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(upper, max(lower, value))
