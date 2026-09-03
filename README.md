# Predictive Risk and Fraud Analytics Framework

A small, reproducible Python framework for transaction ingestion, behavioral feature engineering, fraud model training, and real-time risk scoring.

## How it works

The project follows one simple transaction-scoring flow:

```text
SQLite database
		-> DataPipeline validates and loads transactions
		-> feature engineering creates behavioral signals
		-> XGBoost estimates fraud probability
		-> API maps probability to APPROVE, FLAG, or DENY
```

### 1. Create the data

`src/pipelines/db_setup.py` creates two SQLite tables:

- `users`: user country and account age.
- `transactions`: amount, timestamp, transaction country, and the `is_fraud` training label.

The seed data is deterministic. It contains ordinary transactions plus a small fraud pattern: unusually large, high-velocity transactions from a different country.

### 2. Validate and load it

`DataPipeline` reads the tables with pandas and converts timestamps and amounts to their expected types. Rows with missing amounts, invalid timestamps, or negative amounts receive a `quality_flag` and are removed from the clean training set.

### 3. Build behavioral features

For each user, `src/features/engineering.py` calculates:

- `time_since_last_txn`: hours since the user's previous transaction.
- `daily_txn_count`: number of transactions in the surrounding 24-hour window.
- `amount_vs_average`: current amount divided by the user's previous average amount.
- `country_mismatch`: `1` when transaction and home countries differ, otherwise `0`.

The model uses five numeric columns: `amount`, the three behavioral features above, and `country_mismatch`. Missing or infinite feature values are replaced with `0`.

### 4. Train the models

`src/models/train.py` trains two pipelines:

- **XGBoost classifier**: supervised model trained with the `is_fraud` label. Its fraud probability is used by the API.
- **Isolation Forest**: unsupervised anomaly model trained alongside the classifier for future anomaly-analysis workflows.

Training writes these files to `artifacts/`:

- `fraud_classifier.joblib`
- `isolation_forest.joblib`
- `metrics.json` containing precision, recall, F1, and ROC-AUC.

The example dataset is intentionally small, and the training threshold favors recall to reduce missed fraud. Its metrics should be treated as a pipeline smoke test, not as production model performance.

### 5. Score a transaction through the API

The `/predict` endpoint accepts a transaction, creates the same feature columns used during training, and returns a fraud probability between `0` and `1`:

```bash
curl -X POST http://127.0.0.1:8000/predict \
	-H 'Content-Type: application/json' \
	-d '{"user_id":"u003","amount":2500,"timestamp":"2026-01-01T10:00:00Z","country":"NG"}'
```

Example response:

```json
{"risk_score":0.91,"action":"DENY"}
```

The action thresholds are:

- `APPROVE`: score below `0.35`
- `FLAG`: score from `0.35` up to, but not including, `0.75`
- `DENY`: score `0.75` or higher

The API requires `artifacts/fraud_classifier.joblib`; run the training command before starting the server. The API currently accepts the public transaction fields only, so `country_mismatch` remains `0` unless the feature pipeline is supplied with a separate `home_country` field.

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
