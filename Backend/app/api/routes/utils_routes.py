from fastapi import APIRouter
from app.models.logisticsImpact_model import WeatherLogisticsImpactRequestModel
from app.api.pagination import PaginationDep
from app.services import utils_service


router = APIRouter()

#All utils routes

@router.get("/countries")
def get_countries():
    return utils_service.get_countries()

@router.post("/weather-logistics-impact")
def get_weather_logistics_impact(requestBody: WeatherLogisticsImpactRequestModel):
    return utils_service.weather_logistics_impact(requestBody.event_types)

# Products Catalog
@router.get("/products-catalog")
def get_products_catalog(pagination: PaginationDep):
    return utils_service.get_products_catalog(
        page=pagination.page,
        page_size=pagination.page_size,
    )

@router.get("/products-catalog/{product_id}")
def get_product_detail(product_id: str):
    return utils_service.get_product_detail(product_id)

# Compliance Certifications
@router.get("/compliance-certifications")
def get_compilance_certificates():
    return utils_service.get_compilance_certificates()

@router.get("/compliance-certifications/vendor/{vendor_id}")
def get_certification_by_vendorId(vendor_id: str):
    return utils_service.get_certification_by_vendorId(vendor_id)