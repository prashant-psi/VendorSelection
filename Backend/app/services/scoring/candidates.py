from typing import Any

from app.models.procurement_request import ProcurementRequest
from app.repositories import vendor_scoring_data


def load_scoring_candidates(procurement_request: ProcurementRequest) -> list[dict]:
    """Load vendor metric rows that pass procurement filters for all matched products."""
    product_ids = procurement_request.product_ids or [procurement_request.product_id]
    candidate_rows: list[dict] = []

    for product_id in product_ids:
        eligible_vendors = vendor_scoring_data.fetch_eligible_vendor_products(
            product_id,
            required_quantity=procurement_request.required_quantity,
            budget_usd=procurement_request.budget_usd,
            required_by_date=procurement_request.required_by_date,
        )
        eligible_vendors = _apply_country_filters(eligible_vendors, procurement_request)

        vendor_ids = [vendor["vendor_id"] for vendor in eligible_vendors]
        if not vendor_ids:
            continue

        metric_rows = vendor_scoring_data.fetch_vendor_metric_rows(vendor_ids, product_id)
        for row in metric_rows:
            row["matched_product_id"] = product_id
        candidate_rows.extend(metric_rows)

    return _keep_best_row_per_vendor(candidate_rows)


def load_vendor_metrics_for_product(
    product_id: str,
    *,
    required_quantity: str | float | int | None = None,
    budget_usd: float | None = None,
    required_by_date: str | None = None,
) -> list[dict[str, Any]]:
    """Single-product metric load used by vendor-features API and chat tools."""
    eligible_vendors = vendor_scoring_data.fetch_eligible_vendor_products(
        product_id,
        required_quantity=required_quantity,
        budget_usd=budget_usd,
        required_by_date=required_by_date,
    )
    vendor_ids = [vendor["vendor_id"] for vendor in eligible_vendors]
    return vendor_scoring_data.fetch_vendor_metric_rows(vendor_ids, product_id)


def _apply_country_filters(
    vendors: list[dict],
    procurement_request: ProcurementRequest,
) -> list[dict]:
    filtered = vendors

    if procurement_request.excluded_countries:
        excluded = {country.upper() for country in procurement_request.excluded_countries}
        filtered = [
            vendor
            for vendor in filtered
            if str(vendor.get("country_code", "")).upper() not in excluded
        ]

    if procurement_request.preferred_countries:
        preferred = {country.upper() for country in procurement_request.preferred_countries}
        filtered = [
            vendor
            for vendor in filtered
            if str(vendor.get("country_code", "")).upper() in preferred
        ]

    return filtered


def _keep_best_row_per_vendor(rows: list[dict]) -> list[dict]:
    """When one vendor matches multiple SKUs, keep the row with the highest quality score."""
    best_by_vendor: dict[str, dict] = {}
    for row in rows:
        vendor_id = str(row["vendor_id"])
        existing = best_by_vendor.get(vendor_id)
        if existing is None:
            best_by_vendor[vendor_id] = row
            continue
        current_quality = float(row.get("overall_quality_score") or 0)
        existing_quality = float(existing.get("overall_quality_score") or 0)
        if current_quality >= existing_quality:
            best_by_vendor[vendor_id] = row
    return list(best_by_vendor.values())
