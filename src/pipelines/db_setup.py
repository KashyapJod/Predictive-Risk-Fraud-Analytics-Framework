"""Create and seed the local SQLite transaction database."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import Float, Integer, String, create_engine, text


def create_database(database_url: str = "sqlite:///data/transactions.db") -> None:
    """Create tables and seed deterministic normal and anomalous transactions."""
    engine = create_engine(database_url)
    users = pd.DataFrame(
        [
            {"user_id": "u001", "country": "US", "account_age_days": 920},
            {"user_id": "u002", "country": "GB", "account_age_days": 410},
            {"user_id": "u003", "country": "CA", "account_age_days": 75},
            {"user_id": "u004", "country": "AU", "account_age_days": 1300},
        ]
    )
    start = datetime.now(timezone.utc) - timedelta(days=3)
    rows: list[dict[str, object]] = []
    rng = np.random.default_rng(7)
    countries = {"u001": "US", "u002": "GB", "u003": "CA", "u004": "AU"}
    transaction_id = 1
    for user_id, country in countries.items():
        for offset in range(12):
            amount = round(float(rng.uniform(20, 180)), 2)
            rows.append(
                {
                    "transaction_id": f"t{transaction_id:04d}",
                    "user_id": user_id,
                    "amount": amount,
                    "timestamp": (start + timedelta(hours=offset * 5)).isoformat(),
                    "country": country,
                    "is_fraud": 0,
                }
            )
            transaction_id += 1
    anomaly_time = start + timedelta(hours=58)
    for index in range(5):
        rows.append(
            {
                "transaction_id": f"t{transaction_id:04d}",
                "user_id": "u003",
                "amount": 2400.0 + index * 100,
                "timestamp": (anomaly_time + timedelta(minutes=index)).isoformat(),
                "country": "NG",
                "is_fraud": 1,
            }
        )
        transaction_id += 1
    transactions = pd.DataFrame(rows)
    users.to_sql("users", engine, if_exists="replace", index=False, dtype={"account_age_days": Integer})
    transactions.to_sql(
        "transactions",
        engine,
        if_exists="replace",
        index=False,
        dtype={"amount": Float, "is_fraud": Integer, "country": String(2)},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default="sqlite:///data/transactions.db")
    args = parser.parse_args()
    if args.database.startswith("sqlite:///"):
        Path(args.database.removeprefix("sqlite:///")) .parent.mkdir(parents=True, exist_ok=True)
    create_database(args.database)


if __name__ == "__main__":
    main()