from __future__ import annotations

import argparse
import json
import math
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


DROP_COLUMNS = {"label_mission_impact", "sample_id", "candidate_id", "attack_type"}


def _features(df: pd.DataFrame) -> list[dict]:
    feature_df = df.drop(columns=[col for col in DROP_COLUMNS if col in df.columns])
    return feature_df.fillna(0).to_dict(orient="records")


def _top1_action_match(df: pd.DataFrame, y_pred) -> float:
    working = df[["sample_id", "candidate_id", "label_mission_impact"]].copy()
    working["prediction"] = y_pred
    total = 0
    matched = 0
    for _, group in working.groupby("sample_id"):
        if len(group) < 2:
            continue
        total += 1
        actual = group.sort_values("label_mission_impact", ascending=False).iloc[0]["candidate_id"]
        predicted = group.sort_values("prediction", ascending=False).iloc[0]["candidate_id"]
        if int(actual) == int(predicted):
            matched += 1
    return matched / total if total else 0.0


def train(dataset: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(dataset)
    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["attack_type"] if "attack_type" in df else None,
    )
    x_train = _features(train_df)
    x_test = _features(test_df)
    y_train = train_df["label_mission_impact"].astype(float)
    y_test = test_df["label_mission_impact"].astype(float)

    models = {
        "ridge": Ridge(alpha=1.0),
        "random_forest": RandomForestRegressor(n_estimators=160, random_state=42, min_samples_leaf=3),
        "hist_gradient_boosting": HistGradientBoostingRegressor(random_state=42, max_iter=160),
    }

    results = {}
    fitted = {}
    for name, model in models.items():
        pipe = Pipeline([("vec", DictVectorizer(sparse=False)), ("model", model)])
        pipe.fit(x_train, y_train)
        pred = pipe.predict(x_test)
        results[name] = {
            "mae": float(mean_absolute_error(y_test, pred)),
            "rmse": float(math.sqrt(mean_squared_error(y_test, pred))),
            "r2": float(r2_score(y_test, pred)),
            "top1_action_match_rate": float(_top1_action_match(test_df, pred)),
        }
        fitted[name] = pipe

    best_name = min(results, key=lambda name: results[name]["mae"])
    best = fitted[best_name]
    model_path = output_dir / "aura_impact_model.pkl"
    with model_path.open("wb") as f:
        pickle.dump(best, f)

    metrics = {"best_model": best_name, "models": results}
    metrics_path = output_dir / "aura_impact_model_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    _write_feature_importance(best, output_dir / "aura_feature_importance.png")

    print(f"Best model: {best_name}")
    print(json.dumps(metrics, indent=2))
    print(f"Wrote {model_path}")
    print(f"Wrote {metrics_path}")


def _write_feature_importance(pipe: Pipeline, output: Path) -> None:
    vec = pipe.named_steps["vec"]
    model = pipe.named_steps["model"]
    if not hasattr(model, "feature_importances_"):
        return
    names = vec.get_feature_names_out()
    importances = model.feature_importances_
    ranked = sorted(zip(importances, names), reverse=True)[:15]
    if not ranked:
        return
    values, labels = zip(*ranked)
    plt.figure(figsize=(8, 5))
    plt.barh(list(labels)[::-1], list(values)[::-1])
    plt.title("AURA Impact Predictor Feature Importance")
    plt.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("outputs/datasets/aura_candidate_dataset.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/models"))
    args = parser.parse_args()
    train(args.dataset, args.output_dir)


if __name__ == "__main__":
    main()

