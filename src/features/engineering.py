"""Feature engineering for transaction velocity and amount behavior."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_transaction_features(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return transactions enriched with user-relative behavioral features."""
    required = {"user_id", "amount", "timestamp"}
    missing = required.difference(transactions.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    result = transactions.copy()
    result["timestamp"] = pd.to_datetime(result["timestamp"], utc=True, errors="coerce")
    result = result.sort_values(["user_id", "timestamp"]).reset_index(drop=True)
    grouped = result.groupby("user_id", sort=False)
    result["time_since_last_txn"] = grouped["timestamp"].diff().dt.total_seconds().div(3600).fillna(999.0)
    result["daily_txn_count"] = (
        result.set_index("timestamp")
        .groupby("user_id")["amount"]
        .rolling("24h", closed="both")
        .count()
        .reset_index(level=0, drop=True)
        .to_numpy()
    )
    historical_average = grouped["amount"].transform(lambda values: values.expanding().mean().shift(1))
    result["amount_vs_average"] = result["amount"].div(historical_average.replace(0, np.nan)).fillna(1.0)
    result["country_mismatch"] = 0
    if "country" in result.columns and "home_country" in result.columns:
        result["country_mismatch"] = (result["country"] != result["home_country"]).astype(int)
    return result


def model_features(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return the stable numeric feature matrix used by both models."""
    features = add_transaction_features(transactions)
    columns = ["amount", "time_since_last_txn", "daily_txn_count", "amount_vs_average", "country_mismatch"]
    return features[columns].replace([np.inf, -np.inf], np.nan).fillna(0.0)