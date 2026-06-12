from app.db.pagination import execute_paginated_query
from app.db.connection import execute_query
from typing import Any


def get_products_catalog(page:int =1, page_size:int =20)->dict[str, Any]:
   return execute_paginated_query(
    from_clause="vendor.products_catalog",
    order_by="product_id",
    page=page,
    page_size=page_size,
   )

def get_product_detail(product_id:str)->list[dict[str, Any]]:
    return execute_query("select * from vendor.products_catalog where product_id = :product_id", {"product_id": product_id})

def get_countries()->list[dict[str, Any]]:
    return execute_query("SELECT * FROM vendor.countries")


def weather_logistics_impact(event_types:list[str])->list[dict[str, Any]]:
    return execute_query("select * from vendor.weather_logistics_impact where event_type = ANY(CAST(:event_types AS varchar[]))", {"event_types": event_types})

def get_compilance_certificates()->list[dict[str, Any]]:
    return execute_query("SELECT * FROM vendor.compliance_certifications ORDER BY cert_id")

def get_certification_by_vendorId(vendor_id:str)->list[dict[str, Any]]:
    return execute_query("select * from vendor.compliance_certifications where vendor_id = :vendor_id", {"vendor_id": vendor_id})