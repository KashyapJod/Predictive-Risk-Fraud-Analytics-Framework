import time

from fastapi.testclient import TestClient

from src.api.main import app
from src.api import main as api_main
from src.models.train import train_models
from src.pipelines.db_setup import create_database


def test_root_reports_service_status():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "Sentinel Risk Desk" in response.text
    assert TestClient(app).get("/health").json()["status"] == "ok"


def test_predict_returns_action_and_meets_latency(tmp_path, monkeypatch):
    database = f"sqlite:///{tmp_path / 'api.db'}"
    artifact_dir = tmp_path / "artifacts"
    create_database(database)
    train_models(database, str(artifact_dir))
    monkeypatch.setattr(api_main, "CLASSIFIER_PATH", artifact_dir / "fraud_classifier.joblib")
    monkeypatch.setattr(api_main, "DATABASE_URL", database)
    payload = {"user_id": "u1", "amount": 20, "timestamp": "2026-01-01T10:00:00Z", "country": "US"}
    started = time.perf_counter()
    response = TestClient(app).post("/predict", json=payload)
    elapsed = time.perf_counter() - started
    assert response.status_code == 200
    assert response.json()["action"] in {"APPROVE", "FLAG", "DENY"}
    assert 0 <= response.json()["risk_score"] <= 1
    assert elapsed < 0.2


def test_predict_flags_suspicious_transaction(tmp_path, monkeypatch):
    database = f"sqlite:///{tmp_path / 'api.db'}"
    artifact_dir = tmp_path / "artifacts"
    create_database(database)
    train_models(database, str(artifact_dir))
    monkeypatch.setattr(api_main, "CLASSIFIER_PATH", artifact_dir / "fraud_classifier.joblib")
    monkeypatch.setattr(api_main, "DATABASE_URL", database)
    response = TestClient(app).post(
        "/predict",
        json={"user_id": "u003", "amount": 2500, "timestamp": "2030-01-01T10:00:00Z", "country": "NG"},
    )
    assert response.status_code == 200
    assert response.json()["action"] in {"FLAG", "DENY"}


def test_predict_flags_country_mismatch(tmp_path, monkeypatch):
    database = f"sqlite:///{tmp_path / 'api.db'}"
    artifact_dir = tmp_path / "artifacts"
    create_database(database)
    train_models(database, str(artifact_dir))
    monkeypatch.setattr(api_main, "CLASSIFIER_PATH", artifact_dir / "fraud_classifier.joblib")
    monkeypatch.setattr(api_main, "DATABASE_URL", database)
    response = TestClient(app).post(
        "/predict",
        json={"user_id": "u001", "amount": 120, "timestamp": "2030-01-01T10:00:00Z", "country": "NG"},
    )
    assert response.status_code == 200
    assert response.json()["action"] == "FLAG"
