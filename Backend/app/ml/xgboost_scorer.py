import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import xgboost as xgb

from app.core.numeric import to_float

MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "vendor_ranker.pkl"
META_PATH = MODEL_DIR / "vendor_ranker.meta.json"

FEATURE_COLUMNS = [
    "overall_quality_score",
    "overall_risk_score",
    "overall_esg_score",
    "reliability_score",
    "historical_score",
    "historical_otd_rate",
    "historical_quality_rate",
    "historical_csat_score",
    "on_time_rate",
    "avg_fill_rate_pct",
    "available_capacity",
    "current_utilization_pct",
    "compliance_cert_count",
    "tier",
    "is_preferred",
    "is_strategic",
]

TARGET_COLUMN = "target_score"
MIN_TRAINING_ROWS = 5


def _rows_to_matrix(rows: list[dict[str, Any]], columns: list[str]) -> np.ndarray:
    return np.array(
        [[to_float(row.get(column)) for column in columns] for row in rows],
        dtype=np.float32,
    )


def _save_model(model: xgb.Booster) -> None:
    """Save trained XGBoost Booster as a pickle file."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with MODEL_PATH.open("wb") as file:
        pickle.dump(model, file)


def _load_model() -> xgb.Booster | None:
    """Load trained model from pickle file."""
    if not MODEL_PATH.exists():
        return None
    with MODEL_PATH.open("rb") as file:
        return pickle.load(file)


def _save_metadata(rows_used: int) -> None:
    """Save training metadata next to the model file."""
    metadata = {
        "model_file": MODEL_PATH.name,
        "model_format": "pickle",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "rows_used": rows_used,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def get_model_status() -> dict[str, Any]:
    """Return whether a trained model exists and its metadata."""
    status: dict[str, Any] = {
        "model_exists": model_exists(),
        "model_path": str(MODEL_PATH),
        "model_format": "pickle",
        "metadata_path": str(META_PATH),
        "min_training_rows": MIN_TRAINING_ROWS,
    }
    if META_PATH.exists():
        status["metadata"] = json.loads(META_PATH.read_text(encoding="utf-8"))
    return status


def train_model(training_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Train XGBoost and save to app/ml/models/vendor_ranker.pkl (pickle).

    Target (label): historical overall_score from vendor_historical_performance.
    Features: same columns used during prediction/ranking.
    """
    if len(training_rows) < MIN_TRAINING_ROWS:
        return {
            "status": "skipped",
            "message": f"Need at least {MIN_TRAINING_ROWS} training rows",
            "rows_used": len(training_rows),
            "model_path": str(MODEL_PATH),
        }

    features = _rows_to_matrix(training_rows, FEATURE_COLUMNS)
    targets = np.array(
        [to_float(row.get(TARGET_COLUMN)) for row in training_rows],
        dtype=np.float32,
    )

    dtrain = xgb.DMatrix(features, label=targets, feature_names=FEATURE_COLUMNS)
    model = xgb.train(
        {
            "objective": "reg:squarederror",
            "max_depth": 4,
            "eta": 0.1,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
        },
        dtrain,
        num_boost_round=50,
    )

    _save_model(model)
    _save_metadata(len(training_rows))

    return {
        "status": "success",
        "message": "Model trained and saved as pickle",
        "rows_used": len(training_rows),
        "model_path": str(MODEL_PATH),
        "metadata_path": str(META_PATH),
    }


def predict_vendor_scores(vendors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    model = _load_model()
    if model is None:
        raise FileNotFoundError(
            "XGBoost model not found. Train first: POST /api/v1/scoring/train or run train_model.py"
        )

    matrix = _rows_to_matrix(vendors, FEATURE_COLUMNS)
    dmatrix = xgb.DMatrix(matrix, feature_names=FEATURE_COLUMNS)
    predictions = model.predict(dmatrix)

    scored_vendors = []
    for vendor, score in zip(vendors, predictions):
        vendor_result = dict(vendor)
        vendor_result["ml_score"] = round(float(score), 4)
        vendor_result["scoring_method"] = "xgboost"
        scored_vendors.append(vendor_result)

    return scored_vendors


def model_exists() -> bool:
    return MODEL_PATH.exists()
