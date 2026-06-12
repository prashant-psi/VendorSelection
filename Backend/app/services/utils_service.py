from app.repositories import utils
from typing import Any
#include other necessary services here rahter then product , vendor, users, etc.

def get_countries()->list[dict[str, Any]]:
    return utils.get_countries()

def weather_logistics_impact(event_types:list[str])->list[dict[str, Any]]:
    return utils.weather_logistics_impact(event_types)

#Products Catalog
def get_products_catalog(page:int =1 , page_size:int =20) -> dict[str, Any]:
    return utils.get_products_catalog(page=page, page_size=page_size)

def get_product_detail(product_id: str) -> list[dict[str, Any]]:
    return utils.get_product_detail(product_id)

#Compliance Certifications
def get_compilance_certificates() -> list[dict[str, Any]]:
    return utils.get_compilance_certificates()

def get_certification_by_vendorId(vendor_id: str) -> list[dict[str, Any]]:
    return utils.get_certification_by_vendorId(vendor_id)