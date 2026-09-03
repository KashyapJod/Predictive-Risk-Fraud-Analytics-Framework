# Copilot Work Log

## 2026-09-03

- Expanded `README.md` with the end-to-end architecture, data quality flow, feature definitions, model/artifact roles, API request example, and decision thresholds.
- Built the standard `src`, `tests`, `data`, and `notebooks` project layout.
- Added dependency management in `requirements.txt` and `pyproject.toml`.
- Implemented deterministic SQLite users and transactions, including high-value, high-velocity anomalous rows.
- Implemented ingestion quality flags for missing timestamps, missing amounts, invalid timestamps, and negative amounts.
- Implemented recency, 24-hour transaction count, historical amount ratio, and country mismatch features.
- Implemented Isolation Forest and XGBoost training with joblib artifacts and precision/recall/F1/ROC-AUC metrics.
- Implemented FastAPI `/predict` scoring with `APPROVE`, `FLAG`, and `DENY` actions.
- Added focused tests for imports, database and quality handling, features, model artifacts, and API availability.

## Validation

- Initial validation command: `.venv/bin/pytest tests/test_environment.py -q`.
- Full validation command: `.venv/bin/pytest tests/ -q`.
- Final result: `5 passed, 2 warnings`.
- CLI smoke test generated `data/transactions.db`, model joblib artifacts, and `artifacts/metrics.json`.
- Seeded holdout metrics: precision `0.125`, recall `1.0`, F1 `0.2222222222222222`, ROC-AUC `0.7142857142857143`.
- The warnings are dependency deprecations from the installed FastAPI/Starlette test client stack; no test failed.