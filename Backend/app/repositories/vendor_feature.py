"""Backward-compatible import path for vendor scoring data repository."""

from app.repositories.vendor_scoring_data import (
    fetch_eligible_vendor_products,
    fetch_vendor_metric_rows,
)

get_vendor_products_by_product = fetch_eligible_vendor_products
get_vendor_features_score = fetch_vendor_metric_rows

__all__ = [
    "fetch_eligible_vendor_products",
    "fetch_vendor_metric_rows",
    "get_vendor_features_score",
    "get_vendor_products_by_product",
]
