"""Train anomaly and fraud models and write portable artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.features.engineering import model_features
from src.pipelines.ingestion import DataPipeline


def train_models(database_url: str = "sqlite:///data/transactions.db", artifact_dir: str = "artifacts") -> dict[str, float]:
    output = Path(artifact_dir)
    output.mkdir(parents=True, exist_ok=True)
    data = DataPipeline(database_url).load_transactions()
    if len(data) < 4 or data["is_fraud"].nunique() < 2:
        raise ValueError("Training requires at least two classes and four valid transactions")
    x = model_features(data)
    y = data["is_fraud"].astype(int)
    anomaly_model = Pipeline([("scale", StandardScaler()), ("model", IsolationForest(n_estimators=100, random_state=7, contamination="auto"))])
    anomaly_model.fit(x)
    classifier = Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.08,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=7,
                n_jobs=1,
            )),
        ]
    )
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, stratify=y, random_state=7)
    classifier.fit(x_train, y_train)
    probabilities = classifier.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= 0.01).astype(int)
    metrics = {
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
    }
    joblib.dump(anomaly_model, output / "isolation_forest.joblib")
    joblib.dump(classifier, output / "fraud_classifier.joblib")
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default="sqlite:///data/transactions.db")
    parser.add_argument("--artifacts", default="artifacts")
    args = parser.parse_args()
    print(json.dumps(train_models(args.database, args.artifacts), indent=2))


if __name__ == "__main__":
    main()