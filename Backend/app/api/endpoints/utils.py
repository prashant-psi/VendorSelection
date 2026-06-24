from fastapi import APIRouter, Query

from app.api.pagination import PaginationDep
from app.models.logisticsImpact_model import WeatherLogisticsImpactRequestModel
from app.services import utils_service

router = APIRouter(tags=["utils"])


@router.get("/countries")
def get_countries():
    return utils_service.get_countries()


@router.post("/weather-logistics-impact")
def get_weather_logistics_impact(requestBody: WeatherLogisticsImpactRequestModel):
    return utils_service.weather_logistics_impact(requestBody.event_types)


@router.get("/products-catalog")
def get_products_catalog(pagination: PaginationDep):
    return utils_service.get_products_catalog(page=pagination.page, page_size=pagination.page_size)


@router.get("/products-catalog/{product_id}")
def get_product_detail(product_id: str):
    return utils_service.get_product_detail(product_id)


@router.get("/products-catalog/{product_id}/seasonal-demand")
def get_seasonal_demand(product_id: str):
    return utils_service.get_seasonal_demand(product_id)


@router.get("/products-catalog/{product_id}/vendor-features")
def get_product_vendor_features(
    product_id: str,
    required_quantity: str | None = Query(None, description="Order quantity for MOQ/max-order and budget filters"),
    budget_usd: float | None = Query(None, description="Budget cap in USD"),
    required_by_date: str | None = Query(None, description="Required delivery date (YYYY-MM-DD)"),
):
    return utils_service.get_product_vendor_features(
        product_id,
        required_quantity=required_quantity,
        budget_usd=budget_usd,
        required_by_date=required_by_date,
    )


@router.get("/compliance-certifications")
def get_compilance_certificates():
    return utils_service.get_compilance_certificates()


@router.get("/compliance-certifications/vendor/{vendor_id}")
def get_certification_by_vendorId(vendor_id: str):
    return utils_service.get_certification_by_vendorId(vendor_id)



@router.get("/weight-configs")
def get_weight_configs():
    return utils_service.get_weight_configs()


@router.get("/weight-configs/default")
def get_default_weight_config():
    return utils_service.get_default_weight_config()


@router.get("/weight-configs/{config_id}")
def get_weight_config(config_id: str):
    return utils_service.get_weight_config(config_id)


@router.get("/categories")
def get_categories():
    return utils_service.get_categories()