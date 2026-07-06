from typing import Any

from app.db.connection import execute_query

SQL_ELIGIBLE_VENDOR_PRODUCTS = """
    SELECT
        vp.vendor_id,vp.product_id,vp.unit_price,vp.lead_time_days,vp.min_order_qty,vp.max_order_qty,vp.is_active,
        v.vendor_name,v.country_code,v.is_active AS vendor_is_active,v.blacklist_flag,v.tier,v.is_preferred,v.is_strategic
    FROM vendor.vendor_products vp
    JOIN vendor.vendors v ON v.vendor_id = vp.vendor_id
    WHERE vp.product_id = :product_id
      AND vp.is_active = true
      AND v.is_active = true
      AND v.blacklist_flag = false
      AND (CAST(:min_qty AS numeric) IS NULL OR vp.min_order_qty IS NULL OR vp.min_order_qty <= :min_qty)
      AND (CAST(:max_qty AS numeric) IS NULL OR vp.max_order_qty IS NULL OR vp.max_order_qty >= :max_qty)
      AND (CAST(:budget AS numeric) IS NULL OR CAST(:required_quantity AS numeric) IS NULL OR (vp.unit_price * :required_quantity) <= :budget)
      AND (CAST(:max_lead_days AS integer) IS NULL OR vp.lead_time_days <= :max_lead_days)
"""

SQL_VENDOR_METRIC_ROWS = """
    SELECT
        v.vendor_id,v.vendor_name,v.country_code,v.tier,v.is_preferred,v.is_strategic,
        qs.overall_quality_score,qs.quality_grade,
        rs.overall_risk_score,rs.risk_level,
        esg.overall_esg_score,
        sri.overall_score AS reliability_score,
        vhp.overall_score AS historical_score,vhp.otd_rate AS historical_otd_rate,vhp.quality_rate AS historical_quality_rate,vhp.csat_score AS historical_csat_score,
        dp.on_time_rate,dp.avg_fill_rate_pct,
        pc.available_capacity,pc.current_utilization_pct,pc.max_capacity,
        cc.compliance_cert_count
    FROM vendor.vendors v
    JOIN vendor.vendor_products vp
        ON vp.vendor_id = v.vendor_id
        AND vp.product_id = :product_id
        AND vp.is_active = true
    LEFT JOIN LATERAL (
        SELECT overall_quality_score, quality_grade
        FROM vendor.quality_scores
        WHERE vendor_id = v.vendor_id
          AND product_id = :product_id
        ORDER BY assessment_date DESC
        LIMIT 1
    ) qs ON true
    LEFT JOIN LATERAL (
        SELECT overall_risk_score, risk_level
        FROM vendor.risk_scores
        WHERE vendor_id = v.vendor_id
          AND product_id = :product_id
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
        SELECT overall_score, otd_rate, quality_rate, csat_score
        FROM vendor.vendor_historical_performance
        WHERE vendor_id = v.vendor_id
        ORDER BY period_year DESC, period_month DESC
        LIMIT 1
    ) vhp ON true
    LEFT JOIN LATERAL (
        SELECT
            AVG(CASE WHEN on_time THEN 1.0 ELSE 0.0 END) AS on_time_rate,
            AVG(fill_rate_pct) AS avg_fill_rate_pct
        FROM vendor.delivery_performance
        WHERE vendor_id = v.vendor_id
          AND product_id = :product_id
    ) dp ON true
    LEFT JOIN LATERAL (
        SELECT available_capacity, current_utilization_pct, max_capacity
        FROM vendor.production_capacity
        WHERE vendor_id = v.vendor_id
          AND product_id = :product_id
        ORDER BY period_year DESC, period_quarter DESC, period_month DESC
        LIMIT 1
    ) pc ON true
    LEFT JOIN LATERAL (
        SELECT COUNT(*)::int AS compliance_cert_count
        FROM vendor.compliance_certifications
        WHERE vendor_id = v.vendor_id
          AND is_valid = true
          AND expiry_date >= CURRENT_DATE
    ) cc ON true
    WHERE v.vendor_id = ANY(CAST(:vendor_ids AS uuid[]))
"""

_SQL_VENDORS_WITH_PARTIAL_CAPACITY = """
    SELECT
        vp.vendor_id,
        v.vendor_name,
        vp.max_order_qty,
        vp.min_order_qty,
        vp.unit_price,
        vp.lead_time_days
    FROM vendor.vendor_products vp
    JOIN vendor.vendors v ON v.vendor_id = vp.vendor_id
    WHERE vp.product_id = :product_id
      AND vp.is_active = true
      AND v.is_active = true
      AND v.blacklist_flag = false
      AND vp.max_order_qty IS NOT NULL
      AND CAST(vp.max_order_qty AS numeric) > 0
      AND CAST(vp.max_order_qty AS numeric) < CAST(:required_quantity AS numeric)
    ORDER BY vp.max_order_qty DESC
"""

_SQL_ALL_PRODUCT_VENDORS = """
    SELECT
        vp.vendor_id,
        v.vendor_name,
        vp.min_order_qty,
        vp.max_order_qty,
        vp.lead_time_days,
        vp.unit_price
    FROM vendor.vendor_products vp
    JOIN vendor.vendors v ON v.vendor_id = vp.vendor_id
    WHERE vp.product_id = :product_id
      AND vp.is_active = true
      AND v.is_active = true
      AND v.blacklist_flag = false
    ORDER BY vp.lead_time_days ASC NULLS LAST
"""


def fetch_eligible_vendor_products(
    product_id: str,
    *,
    min_qty: float | None = None,
    max_qty: float | None = None,
    required_quantity: float | None = None,
    budget: float | None = None,
    max_lead_days: int | None = None,
) -> list[dict[str, Any]]:
    """Return vendor-product rows that pass procurement eligibility filters.
    Accepts pre-computed SQL params — use build_procurement_sql_filters() to build them."""
    return execute_query(SQL_ELIGIBLE_VENDOR_PRODUCTS, {
        "product_id": product_id,
        "min_qty": min_qty,
        "max_qty": max_qty,
        "required_quantity": required_quantity,
        "budget": budget,
        "max_lead_days": max_lead_days,
    })


def fetch_vendor_metric_rows(vendor_ids: list[str], product_id: str) -> list[dict[str, Any]]:
    """Return raw scoring metric rows for vendors on a given product."""
    if not vendor_ids:
        return []
    return execute_query(SQL_VENDOR_METRIC_ROWS, {"vendor_ids": vendor_ids, "product_id": product_id})


def fetch_vendors_with_partial_capacity(
    product_id: str,
    required_quantity: float,
) -> list[dict[str, Any]]:
    """Return active vendors whose max_order_qty is less than required_quantity."""
    return execute_query(
        _SQL_VENDORS_WITH_PARTIAL_CAPACITY,
        {"product_id": product_id, "required_quantity": required_quantity},
    )


def fetch_all_product_vendors(product_id: str) -> list[dict[str, Any]]:
    """Return all active vendors for a product with no quantity or lead-time filters."""
    return execute_query(_SQL_ALL_PRODUCT_VENDORS, {"product_id": product_id})
