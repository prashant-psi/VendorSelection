from typing import Any

from app.core.constants import DEFAULT_ML_BLEND_WEIGHT, PREDICT_ML_BLEND_WEIGHT
from app.ml import xgboost_scorer
from app.models.procurement_request import ProcurementRequest
from app.repositories import ml_training

from app.services.procurement.filters import build_procurement_sql_filters

from .advisory import build_filter_advisory, build_quantity_advisory
from .blend import blend_rule_and_ml_scores
from .candidates import load_scoring_candidates
from .rule_engine import compute_rule_scores

__all__ = [
    "DEFAULT_ML_BLEND_WEIGHT",
    "PREDICT_ML_BLEND_WEIGHT",
    "get_merged_vendor_ranking",
    "get_model_status",
    "predict_vendors",
    "rank_vendors",
    "train_xgboost_model",
]


def train_xgboost_model() -> dict[str, Any]:
    training_rows = ml_training.get_ml_training_data()
    return xgboost_scorer.train_model(training_rows)


def get_model_status() -> dict[str, Any]:
    return xgboost_scorer.get_model_status()


def rank_vendors(procurement_request: ProcurementRequest) -> dict[str, Any]:
    """Rank vendors using rule engine with optional ML blend (default 20% ML / 80% rules)."""
    return _build_ranking_response(procurement_request)


def predict_vendors(procurement_request: ProcurementRequest) -> dict[str, Any]:
    """Rank vendors with ML-heavy blend (default 70% ML / 30% rules)."""
    blend = procurement_request.ml_blend_weight or PREDICT_ML_BLEND_WEIGHT
    request = procurement_request.model_copy(update={"ml_blend_weight": blend})
    return _build_ranking_response(request)


def get_merged_vendor_ranking(procurement_request: ProcurementRequest) -> dict[str, Any]:
    """Backward-compatible alias for rank_vendors."""
    return _build_ranking_response(procurement_request)


def _build_ranking_response(procurement_request: ProcurementRequest) -> dict[str, Any]:
    candidate_rows = load_scoring_candidates(procurement_request)
    if not candidate_rows:
        filters = build_procurement_sql_filters(
            required_quantity=procurement_request.required_quantity,
            budget_usd=procurement_request.budget_usd,
            required_by_date=procurement_request.required_by_date,
        )
        filter_advisory = build_filter_advisory(
            procurement_request.product_id,
            required_quantity=filters.get("min_qty"),
            max_lead_days=filters.get("max_lead_days"),
        )
        return {
            "procurement_request": procurement_request.model_dump(),
            "scoring_method": "none",
            "ml_weight": 0.0,
            "rule_weight": 1.0,
            "rankings": [],
            "filter_advisory": filter_advisory,
        }

    vendors = [dict(vendor) for vendor in candidate_rows]
    compute_rule_scores(vendors)

    ml_available = _attach_ml_scores(vendors)
    ml_weight = _clamp_ml_blend_weight(procurement_request.ml_blend_weight)
    blend_rule_and_ml_scores(vendors, ml_available=ml_available, ml_weight=ml_weight)

    vendors.sort(key=lambda vendor: vendor.get("final_score", 0), reverse=True)
    for index, vendor in enumerate(vendors, start=1):
        vendor["rank"] = index

    required_qty = procurement_request.required_quantity
    advisory = build_quantity_advisory(
        procurement_request.product_id,
        required_qty,
        vendors,
    )

    return {
        "procurement_request": procurement_request.model_dump(),
        "scoring_method": "merged" if ml_available else "rule_only",
        "ml_weight": ml_weight if ml_available else 0.0,
        "rule_weight": round(1.0 - ml_weight, 4) if ml_available else 1.0,
        "rankings": vendors,
        "quantity_advisory": advisory,
    }


def _attach_ml_scores(vendor_rows: list[dict[str, Any]]) -> bool:
    if not xgboost_scorer.model_exists():
        return False
    try:
        ml_scored = xgboost_scorer.predict_vendor_scores([dict(vendor) for vendor in vendor_rows])
        ml_by_vendor = {str(row["vendor_id"]): row.get("ml_score") for row in ml_scored}
        for vendor in vendor_rows:
            vendor["ml_score"] = ml_by_vendor.get(str(vendor["vendor_id"]))
        return True
    except FileNotFoundError:
        return False


def _clamp_ml_blend_weight(blend: float | None) -> float:
    weight = blend if blend is not None else DEFAULT_ML_BLEND_WEIGHT
    return min(max(float(weight), 0.0), 1.0)
