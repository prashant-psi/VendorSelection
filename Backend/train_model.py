"""
Train the XGBoost vendor ranking model.

The trained model is saved to:
    app/ml/models/vendor_ranker.pkl      (pickle — used for prediction)
    app/ml/models/vendor_ranker.meta.json (training info)

Requirements:
    - PostgreSQL running with vendor_historical_performance data
    - At least 5 rows with overall_score (see MIN_TRAINING_ROWS in xgboost_scorer.py)
    - .env file with database credentials

Usage (from Backend folder):
    .\\venv\\Scripts\\python.exe train_model.py

Or via API while the server is running:
    POST http://localhost:8000/api/v1/model/train

Check model status:
    GET http://localhost:8000/api/v1/model/status
"""

import json
import sys
from pathlib import Path

# Allow imports from the Backend package when run as a script
_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.ml import xgboost_scorer
from app.repositories import ml_training


def main() -> int:
    print("=" * 60)
    print("Vendor Ranking Model — XGBoost Training")
    print("=" * 60)

    print("\nLoading training data from database...")
    training_rows = ml_training.get_ml_training_data()
    print(f"Rows found: {len(training_rows)}")

    if not training_rows:
        print("\nNo training data found.")
        print("Add rows to vendor.vendor_historical_performance first.")
        return 1

    print("\nTraining model...")
    result = xgboost_scorer.train_model(training_rows)
    print(json.dumps(result, indent=2))

    if result["status"] == "success":
        print("\nDone. Ranking/chat will now use scoring_method: xgboost")
        print(f"Model file: {result['model_path']}")
        return 0

    print("\nTraining skipped. Add more historical performance data and retry.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
