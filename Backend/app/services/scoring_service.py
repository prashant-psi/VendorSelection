from typing import Any

from app.ml import xgboost_scorer
from app.repositories import scoring, vendor_filter
from app.models.procurementRequest_model import ProcurementRequestModel
from app.services import weighted_score


def get_weight_configs() -> list[dict[str, Any]]:
    return scoring.get_weight_configs()


def get_weight_config(config_id: str) -> list[dict[str, Any]]:
    return scoring.get_weight_config(config_id)


def get_default_weight_config() -> list[dict[str, Any]]:
    return scoring.get_default_weight_config()


def get_vendor_latest_scores(vendor_id: str | None = None) -> list[dict[str, Any]]:
    return scoring.get_vendor_latest_scores(vendor_id)


def get_vendor_features(product_id: str) -> list[dict[str, Any]]:
    vendors = vendor_filter.get_vendor_products_by_product(product_id)
    vendor_ids = [vendor["vendor_id"] for vendor in vendors]
    return vendor_filter.get_vendor_features_score(vendor_ids, product_id)


def get_seasonal_demand(product_id: str) -> list[dict[str, Any]]:
    return scoring.get_seasonal_demand(product_id)


def get_quality_scores(vendor_id: str) -> list[dict[str, Any]]:
    return scoring.get_quality_scores(vendor_id)


def get_risk_scores(vendor_id: str) -> list[dict[str, Any]]:
    return scoring.get_risk_scores(vendor_id)


def get_historical_performance(vendor_id: str) -> list[dict[str, Any]]:
    return scoring.get_historical_performance(vendor_id)


def get_recommendations_by_request(request_id: str) -> list[dict[str, Any]]:
    return scoring.get_recommendations_by_request(request_id)


def train_xgboost_model() -> dict[str, Any]:
    training_rows = scoring.get_ml_training_data()
    return xgboost_scorer.train_model(training_rows)


def get_model_status() -> dict[str, Any]:
    return xgboost_scorer.get_model_status()


def predict_vendors(procurement_request: ProcurementRequestModel) -> list[dict[str, Any]]:
    vendors = _get_ranked_vendors(procurement_request, prefer_ml=True)
    return vendors


def rank_vendors(procurement_request: ProcurementRequestModel) -> list[dict[str, Any]]:
    return _get_ranked_vendors(procurement_request, prefer_ml=procurement_request.use_ml)


def _get_ranked_vendors(
    procurement_request: ProcurementRequestModel,
    *,
    prefer_ml: bool,
) -> list[dict[str, Any]]:
    filtered_vendors = vendor_filter.get_vendor_products_by_product(procurement_request.product_id)
    vendor_ids = [vendor["vendor_id"] for vendor in filtered_vendors]

    if procurement_request.excluded_countries:
        excluded = {country.upper() for country in procurement_request.excluded_countries}
        filtered_vendors = [
            vendor for vendor in filtered_vendors
            if str(vendor.get("country_code", "")).upper() not in excluded
        ]
        vendor_ids = [vendor["vendor_id"] for vendor in filtered_vendors]

    if procurement_request.preferred_countries:
        preferred = {country.upper() for country in procurement_request.preferred_countries}
        filtered_vendors = [
            vendor for vendor in filtered_vendors
            if str(vendor.get("country_code", "")).upper() in preferred
        ]
        vendor_ids = [vendor["vendor_id"] for vendor in filtered_vendors]

    vendor_feature_scores = vendor_filter.get_vendor_features_score(
        vendor_ids,
        procurement_request.product_id,
    )

    if not vendor_feature_scores:
        return []

    scored_vendors: list[dict[str, Any]]
    if prefer_ml and xgboost_scorer.model_exists():
        try:
            scored_vendors = xgboost_scorer.predict_vendor_scores(vendor_feature_scores)
        except FileNotFoundError:
            scored_vendors = weighted_score.calculate_weighted_score(vendor_feature_scores)
            for vendor in scored_vendors:
                vendor["scoring_method"] = "weighted"
    else:
        scored_vendors = weighted_score.calculate_weighted_score(vendor_feature_scores)
        for vendor in scored_vendors:
            vendor["scoring_method"] = "weighted"

    scored_vendors.sort(key=lambda vendor: vendor.get("final_score", 0), reverse=True)
    for index, vendor in enumerate(scored_vendors, start=1):
        vendor["rank"] = index

    return scored_vendors
