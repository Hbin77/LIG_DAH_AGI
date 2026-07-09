from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol


class MissionStateLike(Protocol):
    satcom_health: float
    radio_health: float
    lte_health: float
    mesh_health: float
    queue_depth: int
    critical_queue_depth: int
    stale_ratio_window: float
    critical_latency_window: float
    priority_inversion_window: float
    terminal_risk_window: float
    source_trust_drop_window: float
    pace_instability_window: float
    defense_alerted: bool


FEATURE_NAMES = [
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
]

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "tsra_ml_policy.json"
DEFAULT_SKLEARN_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "tsra_sklearn_policy.joblib"
DEFAULT_POLICY_CONFIG_PATH = Path(__file__).resolve().parents[2] / "models" / "tsra_ml_policy_config.json"


@dataclass(frozen=True)
class TrainingSample:
    features: list[float]
    label: int


@dataclass
class LogisticRiskModel:
    feature_names: list[str]
    weights: list[float]
    bias: float
    means: list[float]
    scales: list[float]
    threshold: float
    metrics: dict[str, float]

    def predict_probability(self, features: list[float]) -> float:
        normalized = normalize_features(features, self.means, self.scales)
        logit = self.bias + sum(weight * value for weight, value in zip(self.weights, normalized))
        return sigmoid(logit)

    def predict_label(self, features: list[float]) -> int:
        return int(self.predict_probability(features) >= self.threshold)

    def to_dict(self) -> dict:
        return {
            "model_type": "logistic_regression_binary_risk",
            "feature_names": self.feature_names,
            "weights": self.weights,
            "bias": self.bias,
            "means": self.means,
            "scales": self.scales,
            "threshold": self.threshold,
            "metrics": self.metrics,
            "safety_boundary": {
                "exploit_code": False,
                "operational_rf_parameters": False,
                "synthetic_training_data_only": True,
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LogisticRiskModel":
        return cls(
            feature_names=list(data["feature_names"]),
            weights=[float(value) for value in data["weights"]],
            bias=float(data["bias"]),
            means=[float(value) for value in data["means"]],
            scales=[float(value) for value in data["scales"]],
            threshold=float(data["threshold"]),
            metrics={key: float(value) for key, value in data.get("metrics", {}).items()},
        )


def state_to_features(state: MissionStateLike) -> list[float]:
    return [
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
        1.0 if state.defense_alerted else 0.0,
    ]


def train_model(
    samples: list[TrainingSample],
    *,
    epochs: int = 240,
    learning_rate: float = 0.16,
    l2: float = 0.002,
) -> LogisticRiskModel:
    means, scales = fit_standardizer([sample.features for sample in samples])
    weights = [0.0 for _ in FEATURE_NAMES]
    bias = 0.0

    for _ in range(epochs):
        for sample in samples:
            x = normalize_features(sample.features, means, scales)
            prediction = sigmoid(bias + sum(w * v for w, v in zip(weights, x)))
            error = prediction - sample.label
            for i, value in enumerate(x):
                weights[i] -= learning_rate * (error * value + l2 * weights[i])
            bias -= learning_rate * error

    model = LogisticRiskModel(
        feature_names=FEATURE_NAMES,
        weights=[round(value, 8) for value in weights],
        bias=round(bias, 8),
        means=[round(value, 8) for value in means],
        scales=[round(value, 8) for value in scales],
        threshold=0.50,
        metrics={},
    )
    model.metrics = evaluate_classifier(model, samples)
    return model


def generate_training_samples(count: int, seed: int) -> list[TrainingSample]:
    rng = random.Random(seed)
    samples = []
    for _ in range(count):
        features = synthetic_features(rng)
        label = oracle_label(features)
        samples.append(TrainingSample(features, label))
    rng.shuffle(samples)
    return samples


def split_samples(samples: list[TrainingSample], train_ratio: float = 0.75) -> tuple[list[TrainingSample], list[TrainingSample]]:
    split = int(len(samples) * train_ratio)
    return samples[:split], samples[split:]


def save_model(model: LogisticRiskModel, path: Path = DEFAULT_MODEL_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(model.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def load_model(path: Path = DEFAULT_MODEL_PATH) -> LogisticRiskModel:
    data = json.loads(path.read_text(encoding="utf-8"))
    return LogisticRiskModel.from_dict(data)


def load_sklearn_model(path: Path = DEFAULT_SKLEARN_MODEL_PATH):
    from joblib import load

    return load(path)


def save_policy_config(config: dict[str, float], path: Path = DEFAULT_POLICY_CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "tsra-ml-policy-config/v1",
        "description": "Threshold and fusion parameters selected by mission-simulator policy search.",
        "config": config,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_policy_config(path: Path = DEFAULT_POLICY_CONFIG_PATH) -> dict[str, float]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    config = data.get("config", data)
    return {key: float(value) for key, value in config.items()}


def synthetic_features(rng: random.Random) -> list[float]:
    attacked = rng.random() < 0.55
    if attacked:
        satcom_degradation = rng.uniform(0.25, 0.85)
        queue_pressure = rng.uniform(0.15, 1.0)
        critical_queue = rng.uniform(0.05, 0.75)
        stale_ratio = rng.uniform(0.02, 0.65)
        critical_latency = rng.uniform(0.18, 1.0)
        priority_inversion = rng.uniform(0.0, 0.55)
        terminal_risk = rng.uniform(0.15, 0.75)
        source_drop = rng.uniform(0.08, 0.58)
        pace_instability = rng.uniform(0.0, 0.55)
    else:
        satcom_degradation = rng.uniform(0.0, 0.22)
        queue_pressure = rng.uniform(0.0, 0.30)
        critical_queue = rng.uniform(0.0, 0.25)
        stale_ratio = rng.uniform(0.0, 0.12)
        critical_latency = rng.uniform(0.0, 0.35)
        priority_inversion = rng.uniform(0.0, 0.08)
        terminal_risk = rng.uniform(0.0, 0.22)
        source_drop = rng.uniform(0.0, 0.16)
        pace_instability = rng.uniform(0.0, 0.20)

    radio_health = rng.uniform(0.55, 1.0)
    lte_health = rng.uniform(0.55, 1.0)
    mesh_health = rng.uniform(0.50, 1.0)
    defense_alerted = 1.0 if rng.random() < (0.75 if attacked else 0.10) else 0.0
    return [
        satcom_degradation,
        radio_health,
        lte_health,
        mesh_health,
        queue_pressure,
        critical_queue,
        stale_ratio,
        critical_latency,
        priority_inversion,
        terminal_risk,
        source_drop,
        pace_instability,
        defense_alerted,
    ]


def oracle_label(features: list[float]) -> int:
    (
        satcom_degradation,
        _radio_health,
        _lte_health,
        _mesh_health,
        queue_pressure,
        critical_queue,
        stale_ratio,
        critical_latency,
        priority_inversion,
        terminal_risk,
        source_drop,
        pace_instability,
        _defense_alerted,
    ) = features
    risk = (
        0.22 * satcom_degradation
        + 0.10 * queue_pressure
        + 0.10 * critical_queue
        + 0.18 * stale_ratio
        + 0.20 * critical_latency
        + 0.08 * priority_inversion
        + 0.06 * terminal_risk
        + 0.04 * source_drop
        + 0.02 * pace_instability
    )
    return int(risk >= 0.30 or critical_latency >= 0.72 or stale_ratio >= 0.45)


def evaluate_classifier(model: LogisticRiskModel, samples: list[TrainingSample]) -> dict[str, float]:
    true_positive = false_positive = true_negative = false_negative = 0
    losses = []
    for sample in samples:
        probability = model.predict_probability(sample.features)
        predicted = int(probability >= model.threshold)
        losses.append(log_loss(probability, sample.label))
        if sample.label == 1 and predicted == 1:
            true_positive += 1
        elif sample.label == 0 and predicted == 1:
            false_positive += 1
        elif sample.label == 0 and predicted == 0:
            true_negative += 1
        else:
            false_negative += 1
    total = max(1, len(samples))
    precision = true_positive / max(1, true_positive + false_positive)
    recall = true_positive / max(1, true_positive + false_negative)
    return {
        "accuracy": round((true_positive + true_negative) / total, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(2 * precision * recall / max(1e-9, precision + recall), 4),
        "log_loss": round(sum(losses) / total, 4),
        "samples": float(total),
    }


def fit_standardizer(rows: Iterable[list[float]]) -> tuple[list[float], list[float]]:
    materialized = list(rows)
    columns = list(zip(*materialized))
    means = [sum(column) / len(column) for column in columns]
    scales = []
    for mean, column in zip(means, columns):
        variance = sum((value - mean) ** 2 for value in column) / len(column)
        scales.append(max(math.sqrt(variance), 1e-6))
    return means, scales


def normalize_features(features: list[float], means: list[float], scales: list[float]) -> list[float]:
    return [(value - mean) / scale for value, mean, scale in zip(features, means, scales)]


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def log_loss(probability: float, label: int) -> float:
    probability = min(1.0 - 1e-9, max(1e-9, probability))
    return -(label * math.log(probability) + (1 - label) * math.log(1 - probability))


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(upper, max(lower, value))
