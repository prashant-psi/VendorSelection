from typing import Any

from app.db.connection import execute_query

SQL_GET_WEIGHT_CONFIGS = """
    SELECT *
    FROM vendor.scoring_weight_config
    WHERE is_active = true
    ORDER BY is_default DESC, config_name
"""

SQL_GET_WEIGHT_CONFIG = """
    SELECT *
    FROM vendor.scoring_weight_config
    WHERE config_id = :config_id
"""

SQL_GET_DEFAULT_WEIGHT_CONFIG = """
    SELECT *
    FROM vendor.scoring_weight_config
    WHERE is_default = true AND is_active = true
    LIMIT 1
"""

SQL_GET_VENDOR_LATEST_SCORES = """
    SELECT *
    FROM vendor.v_vendor_latest_scores
    WHERE (:vendor_id IS NULL OR vendor_id = CAST(:vendor_id AS uuid))
    ORDER BY vendor_name
"""

SQL_GET_SEASONAL_DEMAND = """
    SELECT *
    FROM vendor.seasonal_demand
    WHERE product_id = :product_id
    ORDER BY forecast_year, forecast_month
"""

SQL_GET_QUALITY_SCORES = """
    SELECT *
    FROM vendor.quality_scores
    WHERE vendor_id = :vendor_id
    ORDER BY assessment_date DESC
"""

SQL_GET_RISK_SCORES = """
    SELECT *
    FROM vendor.risk_scores
    WHERE vendor_id = :vendor_id
    ORDER BY assessment_date DESC
"""

SQL_GET_HISTORICAL_PERFORMANCE = """
    SELECT *
    FROM vendor.vendor_historical_performance
    WHERE vendor_id = :vendor_id
    ORDER BY period_year DESC, period_month DESC
"""

SQL_GET_RECOMMENDATIONS_BY_REQUEST = """
    SELECT *
    FROM vendor.vendor_recommendations
    WHERE request_id = :request_id
    ORDER BY rank
"""

SQL_GET_ML_TRAINING_DATA = """
    SELECT
        vhp.overall_score AS target_score,
        qs.overall_quality_score,
        rs.overall_risk_score,
        esg.overall_esg_score,
        sri.overall_score AS reliability_score,
        vhp.overall_score AS historical_score,
        vhp.otd_rate AS historical_otd_rate,
        vhp.quality_rate AS historical_quality_rate,
        vhp.csat_score AS historical_csat_score,
        dp.on_time_rate,
        vhp.fill_rate AS avg_fill_rate_pct,
        pc.available_capacity,
        pc.current_utilization_pct,
        cc.compliance_cert_count,
        v.tier,
        CASE WHEN v.is_preferred THEN 1 ELSE 0 END AS is_preferred,
        CASE WHEN v.is_strategic THEN 1 ELSE 0 END AS is_strategic
    FROM vendor.vendor_historical_performance vhp
    JOIN vendor.vendors v ON v.vendor_id = vhp.vendor_id
    LEFT JOIN LATERAL (
        SELECT overall_quality_score
        FROM vendor.quality_scores
        WHERE vendor_id = v.vendor_id
        ORDER BY assessment_date DESC
        LIMIT 1
    ) qs ON true
    LEFT JOIN LATERAL (
        SELECT overall_risk_score
        FROM vendor.risk_scores
        WHERE vendor_id = v.vendor_id AND product_id IS NULL
        ORDER BY assessment_date DESC
        LIMIT 1
    ) rs ON true
    LEFT JOIN LATERAL (
        SELECT overall_esg_score
        FROM vendor.esg_scores
        WHERE vendor_id = v.vendor_id
        ORDER BY assessment_date DESC
        LIMIT 1
    ) esg ON true
    LEFT JOIN LATERAL (
        SELECT overall_score
        FROM vendor.supplier_reliability_index
        WHERE vendor_id = v.vendor_id
        ORDER BY assessment_date DESC
        LIMIT 1
    ) sri ON true
    LEFT JOIN LATERAL (
        SELECT AVG(CASE WHEN on_time THEN 1.0 ELSE 0.0 END) AS on_time_rate
        FROM vendor.delivery_performance
        WHERE vendor_id = v.vendor_id
    ) dp ON true
    LEFT JOIN LATERAL (
        SELECT available_capacity, current_utilization_pct
        FROM vendor.production_capacity
        WHERE vendor_id = v.vendor_id
        ORDER BY period_year DESC, period_quarter DESC
        LIMIT 1
    ) pc ON true
    LEFT JOIN LATERAL (
        SELECT COUNT(*)::int AS compliance_cert_count
        FROM vendor.compliance_certifications
        WHERE vendor_id = v.vendor_id
          AND is_valid = true
          AND expiry_date >= CURRENT_DATE
    ) cc ON true
    WHERE vhp.overall_score IS NOT NULL
"""


def get_weight_configs() -> list[dict[str, Any]]:
    return execute_query(SQL_GET_WEIGHT_CONFIGS)


def get_weight_config(config_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_WEIGHT_CONFIG, {"config_id": config_id})


def get_default_weight_config() -> list[dict[str, Any]]:
    return execute_query(SQL_GET_DEFAULT_WEIGHT_CONFIG)


def get_vendor_latest_scores(vendor_id: str | None = None) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_VENDOR_LATEST_SCORES, {"vendor_id": vendor_id})


def get_seasonal_demand(product_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_SEASONAL_DEMAND, {"product_id": product_id})


def get_quality_scores(vendor_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_QUALITY_SCORES, {"vendor_id": vendor_id})


def get_risk_scores(vendor_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_RISK_SCORES, {"vendor_id": vendor_id})


def get_historical_performance(vendor_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_HISTORICAL_PERFORMANCE, {"vendor_id": vendor_id})


def get_recommendations_by_request(request_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_RECOMMENDATIONS_BY_REQUEST, {"request_id": request_id})


def get_ml_training_data() -> list[dict[str, Any]]:
    return execute_query(SQL_GET_ML_TRAINING_DATA)
