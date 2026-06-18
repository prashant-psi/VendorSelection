from app.db.pagination import execute_paginated_query
from app.db.connection import execute_query
from typing import Any

SQL_GET_WEIGHT_CONFIGS = """
    SELECT *
    FROM vendor.scoring_weight_config
    WHERE is_active = true
    ORDER BY is_default DESC, config_name
"""

SQL_GET_WEIGHT_CONFIG = """
    SELECT *
    FROM vendor.scoring_weight_config
    WHERE config_id = :config_id
"""


SQL_GET_DEFAULT_WEIGHT_CONFIG = """
    SELECT *
    FROM vendor.scoring_weight_config
    WHERE is_default = true AND is_active = true
    LIMIT 1
"""


SQL_GET_VENDOR_LATEST_SCORES = """
    SELECT *
    FROM vendor.v_vendor_latest_scores
    WHERE (:vendor_id IS NULL OR vendor_id = CAST(:vendor_id AS uuid))
    ORDER BY vendor_name
"""



SQL_GET_SEASONAL_DEMAND = """
    SELECT *
    FROM vendor.seasonal_demand
    WHERE product_id = :product_id
    ORDER BY forecast_year, forecast_month
"""

SQL_GET_QUALITY_SCORES = """
    SELECT *
    FROM vendor.quality_scores
    WHERE vendor_id = :vendor_id
    ORDER BY assessment_date DESC
"""

SQL_GET_RISK_SCORES = """
    SELECT *
    FROM vendor.risk_scores
    WHERE vendor_id = :vendor_id
    ORDER BY assessment_date DESC
"""

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


# Weight Config
def get_weight_configs() -> list[dict[str, Any]]:
    return execute_query(SQL_GET_WEIGHT_CONFIGS)


def get_weight_config(config_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_WEIGHT_CONFIG, {"config_id": config_id})


def get_default_weight_config() -> list[dict[str, Any]]:
    return execute_query(SQL_GET_DEFAULT_WEIGHT_CONFIG)


# Vendor Latest Scores
def get_vendor_latest_scores(vendor_id: str | None = None) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_VENDOR_LATEST_SCORES, {"vendor_id": vendor_id})


def get_seasonal_demand(product_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_SEASONAL_DEMAND, {"product_id": product_id})


def get_quality_scores(vendor_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_QUALITY_SCORES, {"vendor_id": vendor_id})


def get_risk_scores(vendor_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_RISK_SCORES, {"vendor_id": vendor_id})
