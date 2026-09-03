import time

from fastapi.testclient import TestClient

from src.api.main import app
from src.api import main as api_main
from src.models.train import train_models
from src.pipelines.db_setup import create_database


def test_predict_returns_action_and_meets_latency(tmp_path, monkeypatch):
    database = f"sqlite:///{tmp_path / 'api.db'}"
    artifact_dir = tmp_path / "artifacts"
    create_database(database)
    train_models(database, str(artifact_dir))
    monkeypatch.setattr(api_main, "CLASSIFIER_PATH", artifact_dir / "fraud_classifier.joblib")
    payload = {"user_id": "u1", "amount": 20, "timestamp": "2026-01-01T10:00:00Z", "country": "US"}
    started = time.perf_counter()
    response = TestClient(app).post("/predict", json=payload)
    elapsed = time.perf_counter() - started
    assert response.status_code == 200
    assert response.json()["action"] in {"APPROVE", "FLAG", "DENY"}
    assert 0 <= response.json()["risk_score"] <= 1
    assert elapsed < 0.2
