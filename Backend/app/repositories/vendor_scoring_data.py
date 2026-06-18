from datetime import date, datetime
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
      AND (:min_qty IS NULL OR vp.min_order_qty IS NULL OR vp.min_order_qty <= :min_qty)
      AND (:max_qty IS NULL OR vp.max_order_qty IS NULL OR vp.max_order_qty >= :max_qty)
      AND (:budget IS NULL OR :required_quantity IS NULL OR (vp.unit_price * :required_quantity) <= :budget)
      AND (:max_lead_days IS NULL OR vp.lead_time_days <= :max_lead_days)
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

_DATE_FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y")


def _parse_quantity(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = float(text)
        return parsed if parsed > 0 else None
    except ValueError:
        return None


def _days_until_delivery(required_by_date: str | None) -> int | None:
    if not required_by_date or not str(required_by_date).strip():
        return None
    target: date | None = None
    for fmt in _DATE_FORMATS:
        try:
            target = datetime.strptime(required_by_date.strip(), fmt).date()
            break
        except ValueError:
            continue
    if target is None:
        return None
    return max((target - date.today()).days, 0)


def build_procurement_sql_filters(
    *,
    required_quantity: str | float | int | None = None,
    budget_usd: float | None = None,
    required_by_date: str | None = None,
) -> dict[str, Any]:
    """Build optional SQL filter parameters from procurement constraints."""
    quantity = _parse_quantity(required_quantity)
    return {
        "min_qty": quantity,
        "max_qty": quantity,
        "required_quantity": quantity,
        "budget": budget_usd,
        "max_lead_days": _days_until_delivery(required_by_date),
    }


def fetch_eligible_vendor_products(
    product_id: str,
    *,
    required_quantity: str | float | int | None = None,
    budget_usd: float | None = None,
    required_by_date: str | None = None,
) -> list[dict[str, Any]]:
    """Return vendor-product rows that pass procurement eligibility filters."""
    params = {
        "product_id": product_id,
        **build_procurement_sql_filters(
            required_quantity=required_quantity,
            budget_usd=budget_usd,
            required_by_date=required_by_date,
        ),
    }
    return execute_query(SQL_ELIGIBLE_VENDOR_PRODUCTS, params)


def fetch_vendor_metric_rows(vendor_ids: list[str], product_id: str) -> list[dict[str, Any]]:
    """Return raw scoring metric rows for vendors on a given product."""
    if not vendor_ids:
        return []

    return execute_query(
        SQL_VENDOR_METRIC_ROWS,
        {"vendor_ids": vendor_ids, "product_id": product_id},
    )
