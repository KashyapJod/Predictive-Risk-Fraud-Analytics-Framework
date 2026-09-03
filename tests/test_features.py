import pandas as pd

from src.features.engineering import add_transaction_features


def test_velocity_and_safe_ratio_features():
    frame = pd.DataFrame(
        [
            {"user_id": "u1", "amount": 0, "timestamp": "2026-01-01T10:00:00Z"},
            {"user_id": "u1", "amount": 10, "timestamp": "2026-01-01T11:00:00Z"},
            {"user_id": "u1", "amount": 30, "timestamp": "2026-01-02T12:00:00Z"},
        ]
    )
    result = add_transaction_features(frame)
    assert result.loc[1, "daily_txn_count"] == 2
    assert result.loc[1, "time_since_last_txn"] == 1
    assert result["amount_vs_average"].notna().all()
