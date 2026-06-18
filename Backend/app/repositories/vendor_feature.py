"""Backward-compatible import path for vendor scoring data repository."""

from app.repositories.vendor_scoring_data import (
    build_procurement_sql_filters,
    fetch_eligible_vendor_products,
    fetch_vendor_metric_rows,
)

build_vendor_product_filter_params = build_procurement_sql_filters
get_vendor_products_by_product = fetch_eligible_vendor_products
get_vendor_features_score = fetch_vendor_metric_rows

__all__ = [
    "build_procurement_sql_filters",
    "build_vendor_product_filter_params",
    "fetch_eligible_vendor_products",
    "fetch_vendor_metric_rows",
    "get_vendor_features_score",
    "get_vendor_products_by_product",
]
