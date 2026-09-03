import importlib


def test_required_libraries_import():
    for module in ("pandas", "numpy", "sklearn", "xgboost", "sqlalchemy", "fastapi", "uvicorn", "pytest"):
        assert importlib.import_module(module)