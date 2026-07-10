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
]

DATASET_GENERATOR_VERSION = "overlap-balanced-v2"
INTERVENTION_RISK_THRESHOLD = 0.18
INTERVENTION_STALE_THRESHOLD = 0.30
INTERVENTION_LATENCY_THRESHOLD = 0.55

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "tsra_ml_policy.json"
DEFAULT_SKLEARN_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "tsra_sklearn_policy.joblib"
DEFAULT_POLICY_CONFIG_PATH = Path(__file__).resolve().parents[2] / "models" / "tsra_ml_policy_config.json"


@dataclass(frozen=True)
class TrainingSample:
    features: list[float]
    label: int


class AblatedRiskModel:
    """Counterfactual model that removes learned risk while preserving policy code."""

    def predict_proba(self, rows: list[list[float]]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in rows]


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
    if count < 2:
        raise ValueError("training sample count must be at least 2")
    rng = random.Random(seed)
    samples: list[TrainingSample] = []
    target_counts = {0: count // 2, 1: count - count // 2}
    observed_counts = {0: 0, 1: 0}
    max_attempts = count * 30
    attempts = 0
    while len(samples) < count and attempts < max_attempts:
        attempts += 1
        features = synthetic_features(rng)
        label = oracle_label(features)
        if observed_counts[label] >= target_counts[label]:
            continue
        samples.append(TrainingSample(features, label))
        observed_counts[label] += 1
    if len(samples) != count:
        raise RuntimeError(
            f"failed to generate balanced samples: requested={count} observed={observed_counts}"
        )
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


def sklearn_backend_name(model: object | None) -> str:
    if model is None:
        return "logistic_fallback"
    class_name = type(model).__name__
    if class_name == "HistGradientBoostingClassifier":
        return "sklearn_hist_gradient_boosting"
    if class_name == "AblatedRiskModel":
        return "ablation_zero_model"
    return f"sklearn_{class_name.lower()}"


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
    regime = rng.random()
    if regime < 0.30:
        risk_values = [rng.betavariate(1.2, 5.0) for _ in range(9)]
    elif regime < 0.65:
        risk_values = [rng.random() for _ in range(9)]
    elif regime < 0.82:
        risk_values = [rng.uniform(0.0, 0.55) for _ in range(9)]
        risk_values[3] = rng.uniform(0.30, 0.58)
    else:
        risk_values = [rng.uniform(0.0, 0.55) for _ in range(9)]
        risk_values[4] = rng.uniform(0.55, 0.82)

    (
        satcom_degradation,
        queue_pressure,
        critical_queue,
        stale_ratio,
        critical_latency,
        priority_inversion,
        terminal_risk,
        source_drop,
        pace_instability,
    ) = risk_values
    radio_health = rng.uniform(0.45, 1.0)
    lte_health = rng.uniform(0.45, 1.0)
    mesh_health = rng.uniform(0.45, 1.0)
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
    ]


def oracle_label(features: list[float]) -> int:
    return int(
        oracle_risk_score(features) >= INTERVENTION_RISK_THRESHOLD
        or features[7] >= INTERVENTION_LATENCY_THRESHOLD
        or features[6] >= INTERVENTION_STALE_THRESHOLD
    )


def oracle_risk_score(features: list[float]) -> float:
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
    ) = features
    return (
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
