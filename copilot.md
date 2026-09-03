# Copilot Work Log

## 2026-09-03

- Verified the project: clean git state, required artifacts present, diagnostics clear, and the test suite initially passed with `5 passed, 2 warnings`.
- Found and fixed an API behavior gap where single-row scoring hid user history and a suspicious transaction could be approved.
- The API now loads transaction history and home country, computes contextual features, and applies explainable guardrails for amount/country mismatch and high velocity.
- Added a suspicious-transaction regression test. Final validation: `6 passed, 2 warnings`; live smoke test on port `8001` returned `risk_score: 0.75` and `action: DENY`.
- Added `GET /` health response so opening the base local URL no longer returns `404 Not Found`.
- Expanded `README.md` with the end-to-end architecture, data quality flow, feature definitions, model/artifact roles, API request example, and decision thresholds.
- Built the standard `src`, `tests`, `data`, and `notebooks` project layout.
- Added dependency management in `requirements.txt` and `pyproject.toml`.
- Implemented deterministic SQLite users and transactions, including high-value, high-velocity anomalous rows.
- Implemented ingestion quality flags for missing timestamps, missing amounts, invalid timestamps, and negative amounts.
- Implemented recency, 24-hour transaction count, historical amount ratio, and country mismatch features.
- Implemented Isolation Forest and XGBoost training with joblib artifacts and precision/recall/F1/ROC-AUC metrics.
- Implemented FastAPI `/predict` scoring with `APPROVE`, `FLAG`, and `DENY` actions.
- Added focused tests for imports, database and quality handling, features, model artifacts, and API availability.
- Added `docs/PROJECT_WORKFLOW.md` with the complete project workflow, data schemas, feature calculations, model lifecycle, API sequence, tests, troubleshooting, and production extension guidance.
- Expanded the database seed to 660 transactions across 20 users and 60 mixed fraud examples.
- Fixed training feature/label ordering and added home-country joins; final seeded metrics are precision `0.929`, recall `0.722`, F1 `0.813`, and ROC-AUC `0.915`.
- Decoupled the synthetic fraud archetypes across amount, velocity, location, and subtle cases. Current metrics are precision `0.923`, recall `0.667`, F1 `0.774`, and ROC-AUC `0.923`; amount importance is `0.105` while recency and velocity lead.
- Audited API decision bands with multiple cases; corrected the routine sample to user `u001` home country `GB`, added unknown-user `404` handling, and added explicit approve/flag/deny regression coverage.
- Improved dashboard readability by formatting user dropdown choices with home countries and country choices with full names; verified the live page and all `9` tests.
- Added the Sentinel Risk Desk browser interface at `/`, including sample scenarios, risk visualization, decision guidance, and session history.
- Replaced free-text user and country fields with dropdown selectors populated with all seeded users and supported country codes.
- Added a country-mismatch `FLAG` path so moderate unexpected-location transactions have a reproducible middle-risk example.

## Validation

- Initial validation command: `.venv/bin/pytest tests/test_environment.py -q`.
- Full validation command: `.venv/bin/pytest tests/ -q`.
- Final result before this update: `7 passed, 2 warnings`.
- CLI smoke test generated `data/transactions.db`, model joblib artifacts, and `artifacts/metrics.json`.
- Previous seeded holdout metrics are retained above as historical context; the current seeded holdout is precision `0.9285714285714286`, recall `0.7222222222222222`, F1 `0.8125`, ROC-AUC `0.9152777777777777`.
- The warnings are dependency deprecations from the installed FastAPI/Starlette test client stack; no test failed.