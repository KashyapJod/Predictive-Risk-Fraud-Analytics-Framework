import pandas as pd
from sqlalchemy import create_engine, inspect

from src.pipelines.db_setup import create_database
from src.pipelines.ingestion import DataPipeline


def test_database_tables_and_quality_filter(tmp_path):
    url = f"sqlite:///{tmp_path / 'test.db'}"
    create_database(url)
    initial = DataPipeline(url).load_transactions()
    assert len(initial) == 660
    assert 0.04 < initial["is_fraud"].mean() < 0.10
    assert set(inspect(create_engine(url)).get_table_names()) == {"transactions", "users"}
    engine = create_engine(url)
    pd.DataFrame([{ "transaction_id": "bad", "user_id": "u001", "amount": None, "timestamp": None, "country": "US", "is_fraud": 0 }]).to_sql("transactions", engine, if_exists="append", index=False)
    loaded = DataPipeline(url).load_transactions()
    assert loaded["quality_flag"].eq(False).all()
