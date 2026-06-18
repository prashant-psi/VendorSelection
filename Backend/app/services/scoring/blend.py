from typing import Any

from app.core.numeric import to_float


def blend_rule_and_ml_scores(
    vendor_rows: list[dict[str, Any]],
    *,
    ml_available: bool,
    ml_weight: float,
) -> None:
    """Normalize rule and ML scores within the candidate pool and set `final_score`."""
    rule_min, rule_max = _score_bounds(vendor_rows, "rule_score")

    if not ml_available:
        for vendor in vendor_rows:
            vendor["final_score"] = round(to_float(vendor.get("rule_score")), 4)
            vendor["score_source"] = "rule_only"
        return

    ml_min, ml_max = _score_bounds(vendor_rows, "ml_score")
    rule_weight = 1.0 - ml_weight

    for vendor in vendor_rows:
        normalized_rule = _normalize_score(vendor.get("rule_score"), rule_min, rule_max)
        normalized_ml = _normalize_score(vendor.get("ml_score"), ml_min, ml_max)
        vendor["final_score"] = round((ml_weight * normalized_ml) + (rule_weight * normalized_rule), 4)
        vendor["score_source"] = "rule_and_ml"


def _score_bounds(vendor_rows: list[dict[str, Any]], key: str) -> tuple[float, float]:
    values = [to_float(vendor[key]) for vendor in vendor_rows if vendor.get(key) is not None]
    if not values:
        return 0.0, 0.0
    return min(values), max(values)


def _normalize_score(value: Any, min_value: float, max_value: float) -> float:
    if value is None:
        return 0.0
    number = to_float(value)
    if max_value == min_value:
        return 1.0
    return (number - min_value) / (max_value - min_value)
