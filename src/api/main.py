"""FastAPI endpoint for real-time transaction risk scoring."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.features.engineering import model_features
from src.pipelines.ingestion import DataPipeline


class Transaction(BaseModel):
    user_id: str
    amount: float = Field(gt=0)
    timestamp: str
    country: str = Field(min_length=2, max_length=2)


class Prediction(BaseModel):
    risk_score: float
    action: str


app = FastAPI(title="Predictive Risk and Fraud Analytics API", version="0.1.0")
CLASSIFIER_PATH = Path("artifacts/fraud_classifier.joblib")
DATABASE_URL = "sqlite:///data/transactions.db"


@app.post("/predict", response_model=Prediction)
def predict(transaction: Transaction) -> Prediction:
    if not CLASSIFIER_PATH.exists():
        raise HTTPException(status_code=503, detail="Model artifacts are not available")
    pipeline = DataPipeline(DATABASE_URL)
    history = pipeline.load_transactions()
    users = pipeline.load_users()
    user_history = history.loc[history["user_id"] == transaction.user_id].copy()
    home_country = users.loc[users["user_id"] == transaction.user_id, "country"]
    current = pd.DataFrame([transaction.model_dump()])
    current["home_country"] = home_country.iloc[0] if not home_country.empty else ""
    feature_rows = pd.concat([user_history, current], ignore_index=True)
    current_features = model_features(feature_rows).tail(1)
    risk_score = float(joblib.load(CLASSIFIER_PATH).predict_proba(current_features)[0, 1])
    latest_features = current_features.iloc[0]
    if latest_features["amount_vs_average"] >= 2 and latest_features["country_mismatch"] == 1:
        risk_score = max(risk_score, 0.75)
    elif latest_features["daily_txn_count"] >= 4:
        risk_score = max(risk_score, 0.5)
    action = "DENY" if risk_score >= 0.75 else "FLAG" if risk_score >= 0.35 else "APPROVE"
    return Prediction(risk_score=round(risk_score, 6), action=action)