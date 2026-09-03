"""FastAPI endpoint for real-time transaction risk scoring."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.features.engineering import model_features


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


@app.post("/predict", response_model=Prediction)
def predict(transaction: Transaction) -> Prediction:
    if not CLASSIFIER_PATH.exists():
        raise HTTPException(status_code=503, detail="Model artifacts are not available")
    model_input = pd.DataFrame([transaction.model_dump()])
    risk_score = float(joblib.load(CLASSIFIER_PATH).predict_proba(model_features(model_input))[0, 1])
    action = "DENY" if risk_score >= 0.75 else "FLAG" if risk_score >= 0.35 else "APPROVE"
    return Prediction(risk_score=round(risk_score, 6), action=action)