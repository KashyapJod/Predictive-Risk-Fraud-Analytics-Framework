# Predictive Risk and Fraud Analytics Framework

A small, reproducible Python framework for transaction ingestion, behavioral feature engineering, fraud model training, and real-time risk scoring.

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m src.pipelines.db_setup
.venv/bin/python -m src.models.train
.venv/bin/uvicorn src.api.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Open `/docs` for the interactive OpenAPI client.

## Test

```bash
.venv/bin/pytest -q
```

## Layout

- `src/pipelines`: SQLite schema, deterministic mock data, and quality-aware loading.
- `src/features`: velocity, recency, and user-relative amount features.
- `src/models`: model training and JSON/joblib artifacts.
- `src/api`: FastAPI `/predict` endpoint returning `APPROVE`, `FLAG`, or `DENY`.
- `tests`: focused unit and integration checks.

The classifier uses a weighted XGBoost model and Isolation Forest is trained alongside it for supervised and unsupervised detection. The public model input deliberately stays small and numeric so the artifacts remain portable.
