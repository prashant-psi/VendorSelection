from typing import Any

# Only these columns are normalized. Identity fields (vendor_name, country_code, etc.) stay unchanged.
SCORE_COLUMNS: dict[str, dict[str, Any]] = {
    "quality": {"column": "overall_quality_score", "invert": False},
    "risk": {"column": "overall_risk_score", "invert": True},
    "esg": {"column": "overall_esg_score", "invert": False},
    "reliability": {"column": "reliability_score", "invert": False},
    "historical": {"column": "historical_score", "invert": False},
    "delivery": {"column": "on_time_rate", "invert": False},
    "capacity": {"column": "available_capacity", "invert": False},
    "compliance": {"column": "compliance_cert_count", "invert": False},
}


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def normalize_value(
    value: Any,
    min_val: float,
    max_val: float,
    *,
    invert: bool = False,
) -> float | None:
    """Convert one raw score to 0.0-1.0 within the candidate pool."""
    number = _to_float(value)
    if number is None:
        return None
    if max_val == min_val:
        return 1.0

    normalized = (number - min_val) / (max_val - min_val)
    if invert:
        normalized = 1.0 - normalized
    return round(normalized, 4)


def normalize_vendor_scores(
    vendors: list[dict[str, Any]],
    score_columns: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Add norm_<dimension> keys for selected score columns only.

    Example:
        normalized = normalize_vendor_scores(vendor_feature_scores)
        normalized[0]["norm_quality"]  # 0.0 - 1.0
        normalized[0]["vendor_name"]   # unchanged
    """
    columns = score_columns or SCORE_COLUMNS
    result = [dict(vendor) for vendor in vendors]

    for dimension, config in columns.items():
        column_name = config["column"]
        invert = config.get("invert", False)

        raw_values = [
            _to_float(vendor[column_name])
            for vendor in result
            if vendor.get(column_name) is not None
        ]
        if not raw_values:
            continue

        min_val = min(raw_values)
        max_val = max(raw_values)

        for vendor in result:
            vendor[f"norm_{dimension}"] = normalize_value(
                vendor.get(column_name),
                min_val,
                max_val,
                invert=invert,
            )

    return result
