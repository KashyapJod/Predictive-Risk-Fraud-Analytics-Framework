"""Create and seed the local SQLite transaction database."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import Float, Integer, String, create_engine


def create_database(database_url: str = "sqlite:///data/transactions.db") -> None:
    """Create tables and seed deterministic normal and anomalous transactions."""
    engine = create_engine(database_url)
    countries = ["US", "GB", "CA", "AU", "DE", "FR", "SG", "JP", "BR", "IN"]
    users = pd.DataFrame(
        [
            {"user_id": f"u{index:03d}", "country": countries[index % len(countries)], "account_age_days": 60 + index * 47}
            for index in range(1, 21)
        ]
    )
    start = datetime.now(timezone.utc) - timedelta(days=30)
    rows: list[dict[str, object]] = []
    rng = np.random.default_rng(7)
    transaction_id = 1
    user_countries = dict(zip(users["user_id"], users["country"], strict=True))
    for user_id, country in user_countries.items():
        for offset in range(30):
            amount = round(float(np.clip(rng.normal(105, 38), 12, 260)), 2)
            rows.append(
                {
                    "transaction_id": f"t{transaction_id:04d}",
                    "user_id": user_id,
                    "amount": amount,
                    "timestamp": (start + timedelta(hours=offset * 23 + int(rng.integers(0, 5)))).isoformat(),
                    "country": country,
                    "is_fraud": 0,
                }
            )
            transaction_id += 1
    fraud_users = list(user_countries)[::2]
    for fraud_index, user_id in enumerate(fraud_users):
        country = user_countries[user_id]
        anomaly_time = start + timedelta(days=25, hours=fraud_index)
        for index in range(6):
            subtle = fraud_index % 4 == 0
            mismatch = not subtle and fraud_index % 3 != 0
            amount = round(float(rng.uniform(260, 620)), 2) if not subtle else round(float(rng.uniform(40, 180)), 2)
            transaction_time = anomaly_time + timedelta(minutes=index * 4)
            if subtle:
                transaction_time = start + timedelta(days=10 + index * 3 + fraud_index)
            rows.append(
                {
                    "transaction_id": f"t{transaction_id:05d}",
                    "user_id": user_id,
                    "amount": amount,
                    "timestamp": transaction_time.isoformat(),
                    "country": "NG" if mismatch else country,
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