from typing import Any

POSITIVE_FEATURES = {
    "overall_quality_score": 0.25,
    "reliability_score": 0.20,
    "historical_score": 0.15,
    "overall_esg_score": 0.15,
    "historical_quality_rate": 0.10,
    "historical_otd_rate": 0.10,
    "historical_csat_score": 0.05,
}

NEGATIVE_FEATURES = {
    "overall_risk_score": 0.10
}


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def calculate_weighted_score(vendor_feature_scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for vendor in vendor_feature_scores:
        weighted_score = 0.0
        for feature, weight in POSITIVE_FEATURES.items():
            weighted_score += _to_float(vendor.get(feature)) * weight

        for feature, weight in NEGATIVE_FEATURES.items():
            weighted_score -= _to_float(vendor.get(feature)) * weight

        vendor["final_score"] = round(weighted_score, 4)

    return vendor_feature_scores