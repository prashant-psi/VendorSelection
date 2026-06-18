from typing import Any

from app.db.connection import execute_query


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


def get_ml_training_data() -> list[dict[str, Any]]:
    return execute_query(SQL_GET_ML_TRAINING_DATA)
