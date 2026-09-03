# Copilot Agent Execution Plan: Predictive Risk & Fraud Analytics Framework

This document outlines the step-by-step instructions for an AI coding agent (like GitHub Copilot Workspace) to build the Predictive Risk & Fraud Analytics Framework. Follow the phases sequentially. For each phase, generate the code, write the corresponding tests, and run validations before proceeding.

## Project Overview
**Goal:** Build a scalable machine learning framework in Python to identify anomalous transaction patterns, mitigate fraud, and predict financial risks.
**Key Components:** 
- Real-time data ingestion pipelines (SQL/Cloud).
- Scalable ML anomaly detection framework.
- Automated testing and KPI reporting.

---

## Phase 1: Repository Setup & Infrastructure Configuration
**Objective:** Establish the project structure and dependency management.

1. **Step 1: Directory Structure**
   - Create a standard Python project layout:
     - `src/` (source code: pipelines, features, models, api)
     - `tests/` (unit and integration tests)
     - `data/` (raw and processed mock data)
     - `notebooks/` (EDA and hypothesis testing)
2. **Step 2: Dependency Management**
   - Create a `requirements.txt` containing: `pandas`, `numpy`, `scikit-learn`, `xgboost`, `sqlalchemy`, `fastapi`, `uvicorn`, `pytest`, `pytest-mock`.
3. **Validation & Testing:**
   - **Action:** Create `tests/test_environment.py` to assert that all required libraries can be imported successfully.
   - **Run:** `pytest tests/test_environment.py`. Do not proceed until tests pass.

---

## Phase 2: Data Ingestion & Pipeline Construction
**Objective:** Automate real-time data ingestion and ensure data quality and regulatory compliance.

1. **Step 1: Database Schema & Mock Data**
   - Write a Python script using SQLAlchemy (`src/pipelines/db_setup.py`) to create an SQLite database with two tables: `transactions` and `users`.
   - Generate mock enterprise data featuring standard transactions and injected anomalous patterns (e.g., high-velocity transactions, geolocation mismatches).
2. **Step 2: Ingestion Pipeline**
   - Create `src/pipelines/ingestion.py` with a class `DataPipeline` that loads data from the database into Pandas DataFrames.
   - Implement data quality checks (e.g., handling missing values, checking data types, ensuring non-negative transaction amounts).
3. **Validation & Testing:**
   - **Action:** Write `tests/test_pipelines.py`.
   - **Test Cases:**
     - Verify database connection and table creation.
     - Assert that the ingestion pipeline drops or flags rows with null critical fields (e.g., `amount`, `timestamp`).
   - **Run:** `pytest tests/test_pipelines.py`

---

## Phase 3: Feature Engineering
**Objective:** Transform raw data into predictive signals for the ML models.

1. **Step 1: Time-Series & Velocity Features**
   - Create `src/features/engineering.py`.
   - Implement functions to calculate:
     - `time_since_last_txn`: Time difference between current and previous transaction for a user.
     - `daily_txn_count`: Rolling count of transactions in the last 24 hours.
     - `amount_vs_average`: Ratio of current transaction amount to the user's historical average.
2. **Validation & Testing:**
   - **Action:** Write `tests/test_features.py`.
   - **Test Cases:**
     - Mock a user's transaction history and assert that `daily_txn_count` aggregates correctly.
     - Ensure no division-by-zero errors occur in ratio calculations.
   - **Run:** `pytest tests/test_features.py`

---

## Phase 4: Machine Learning Framework (Risk & Fraud Detection)
**Objective:** Build, train, and evaluate the predictive models.

1. **Step 1: Model Training Pipeline**
   - Create `src/models/train.py`.
   - Implement a modular training script using `scikit-learn` Pipeline.
   - Train two models: 
     - **Isolation Forest** (for unsupervised anomaly detection).
     - **XGBoost Classifier** (for supervised fraud prediction, assuming labels exist in the mock data).
2. **Step 2: Model Evaluation & KPIs**
   - Calculate precision, recall, F1-score, and ROC-AUC. 
   - Optimize for high recall (minimizing false negatives for fraud).
   - Output an artifact: `metrics.json`.
3. **Validation & Testing:**
   - **Action:** Write `tests/test_models.py`.
   - **Test Cases:**
     - Ensure the training script outputs serialized model files (e.g., `.pkl` or `.joblib`).
     - Assert that the generated `metrics.json` contains valid numeric scores between 0 and 1.
   - **Run:** `pytest tests/test_models.py`

---

## Phase 5: Real-Time API for Actionable Recommendations
**Objective:** Expose the model for real-time scoring to enable smarter financial decisions.

1. **Step 1: FastAPI Application**
   - Create `src/api/main.py` using FastAPI.
   - Define a `/predict` POST endpoint that accepts JSON transaction data.
   - The endpoint must pass the data through the feature engineering pipeline, query the trained model, and return a risk score (0.0 to 1.0) and a recommended action (`APPROVE`, `FLAG`, `DENY`).
2. **Validation & Testing:**
   - **Action:** Write `tests/test_api.py` using FastAPI's `TestClient`.
   - **Test Cases:**
     - Send a payload for a normal transaction and assert status 200 with an `APPROVE` recommendation.
     - Send a payload with known anomalous features and assert a `FLAG` or `DENY` recommendation.
     - Ensure latency constraints are met (e.g., response time < 200ms).
   - **Run:** `pytest tests/test_api.py`

---

## Phase 6: Documentation & Agile Wrap-up
**Objective:** Document findings and prepare the project for stakeholder review.

1. **Step 1: Readme & Runbook**
   - Generate a comprehensive `README.md` detailing how to install dependencies, initialize the database, train the models, and start the API.
2. **Step 2: Final Integration Test**
   - Run the entire test suite `pytest tests/ -v` to ensure all components interact flawlessly.
   - Agent must report the final test coverage and any edge cases handled during implementation.
