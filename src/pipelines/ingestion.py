"""Load transactions and apply critical data quality rules."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sqlalchemy import create_engine


@dataclass
class DataPipeline:
    database_url: str = "sqlite:///data/transactions.db"

    def load_transactions(self, clean: bool = True) -> pd.DataFrame:
        frame = pd.read_sql("SELECT * FROM transactions", create_engine(self.database_url))
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
        frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce")
        frame["quality_flag"] = self.quality_flags(frame).astype(bool)
        if clean:
            frame = frame.loc[~frame["quality_flag"]].copy()
        return frame.reset_index(drop=True)

    def load_users(self) -> pd.DataFrame:
        return pd.read_sql("SELECT * FROM users", create_engine(self.database_url))

    @staticmethod
    def quality_flags(frame: pd.DataFrame) -> pd.Series:
        required = frame["amount"].isna() | frame["timestamp"].isna()
        return required | (frame["amount"] < 0)