from typing import Any

from app.core.numeric import to_float

RULE_WEIGHTS_POSITIVE = {
    "overall_quality_score": 0.25,
    "reliability_score": 0.20,
    "historical_score": 0.15,
    "overall_esg_score": 0.15,
    "historical_quality_rate": 0.10,
    "historical_otd_rate": 0.10,
    "historical_csat_score": 0.05,
}

RULE_WEIGHTS_NEGATIVE = {
    "overall_risk_score": 0.10,
}


def compute_rule_scores(vendor_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply fixed rule-engine weights and write `rule_score` on each vendor row."""
    for vendor in vendor_rows:
        score = 0.0
        for metric, weight in RULE_WEIGHTS_POSITIVE.items():
            score += to_float(vendor.get(metric)) * weight
        for metric, weight in RULE_WEIGHTS_NEGATIVE.items():
            score -= to_float(vendor.get(metric)) * weight
        vendor["rule_score"] = round(score, 4)
    return vendor_rows