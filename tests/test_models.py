import json

from src.models.train import train_models
from src.pipelines.db_setup import create_database


def test_training_writes_models_and_metrics(tmp_path):
    database = f"sqlite:///{tmp_path / 'train.db'}"
    artifact_dir = tmp_path / "artifacts"
    create_database(database)
    metrics = train_models(database, str(artifact_dir))
    assert {"precision", "recall", "f1", "roc_auc"} == metrics.keys()
    assert all(0 <= value <= 1 for value in metrics.values())
    assert metrics["recall"] < 1.0
    assert metrics["roc_auc"] > 0.5
    assert (artifact_dir / "isolation_forest.joblib").exists()
    assert (artifact_dir / "fraud_classifier.joblib").exists()
    assert json.loads((artifact_dir / "metrics.json").read_text()) == metrics