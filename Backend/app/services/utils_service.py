from typing import Any

from app.repositories import utils
from app.services.scoring.candidates import load_vendor_metrics_for_product


def get_countries() -> list[dict[str, Any]]:
    return utils.get_countries()


def weather_logistics_impact(event_types: list[str]) -> list[dict[str, Any]]:
    return utils.weather_logistics_impact(event_types)


def get_products_catalog(page: int = 1, page_size: int = 20) -> dict[str, Any]:
    return utils.get_products_catalog(page=page, page_size=page_size)


def get_product_detail(product_id: str) -> list[dict[str, Any]]:
    return utils.get_product_detail(product_id)


def get_seasonal_demand(product_id: str) -> list[dict[str, Any]]:
    return utils.get_seasonal_demand(product_id)


def get_product_vendor_features(
    product_id: str,
    *,
    required_quantity: str | float | int | None = None,
    budget_usd: float | None = None,
    required_by_date: str | None = None,
) -> list[dict[str, Any]]:
    return load_vendor_metrics_for_product(
        product_id,
        required_quantity=required_quantity,
        budget_usd=budget_usd,
        required_by_date=required_by_date,
    )


def get_compilance_certificates() -> list[dict[str, Any]]:
    return utils.get_compilance_certificates()


def get_certification_by_vendorId(vendor_id: str) -> list[dict[str, Any]]:
    return utils.get_certification_by_vendorId(vendor_id)


def get_weight_configs() -> list[dict[str, Any]]:
    return utils.get_weight_configs()


def get_weight_config(config_id: str) -> list[dict[str, Any]]:
    return utils.get_weight_config(config_id)


def get_default_weight_config() -> list[dict[str, Any]]:
    return utils.get_default_weight_config()
