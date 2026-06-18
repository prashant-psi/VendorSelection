from typing import Any

from app.repositories import utils, vendors


def get_vendors(page: int = 1, page_size: int = 20) -> dict[str, Any]:
    return vendors.get_vendors(page=page, page_size=page_size)


def get_vendor(vendor_id: str) -> list[dict[str, Any]]:
    return vendors.get_vendor(vendor_id)


def get_vendors_by_ids(vendors_ids: list[str]) -> list[dict[str, Any]]:
    return vendors.get_vendors_by_ids(vendors_ids)


def get_vendor_products(page: int = 1, page_size: int = 20) -> dict[str, Any]:
    return vendors.get_vendor_products(page=page, page_size=page_size)


def get_vendor_recommendations(page: int = 1, page_size: int = 20) -> dict[str, Any]:
    return vendors.get_vendor_recommendations(page=page, page_size=page_size)


def get_recommendations_by_request(request_id: str) -> list[dict[str, Any]]:
    return vendors.get_recommendations_by_request(request_id)


def get_vendor_latest_scores(vendor_id: str | None = None) -> list[dict[str, Any]]:
    return utils.get_vendor_latest_scores(vendor_id)


def get_quality_scores(vendor_id: str) -> list[dict[str, Any]]:
    return utils.get_quality_scores(vendor_id)


def get_risk_scores(vendor_id: str) -> list[dict[str, Any]]:
    return utils.get_risk_scores(vendor_id)


def get_historical_performance(vendor_id: str) -> list[dict[str, Any]]:
    return vendors.get_historical_performance(vendor_id)


def get_categories() -> list[dict[str, Any]]:
    return vendors.categories()


def get_vendor_by_category_names(category_names: list[str]) -> list[dict[str, Any]]:
    return vendors.get_vendor_by_category_names(category_names)


def get_vendor_production_capacity(vendor_id: str) -> list[dict[str, Any]]:
    return vendors.get_vendor_production_capacity(vendor_id)
