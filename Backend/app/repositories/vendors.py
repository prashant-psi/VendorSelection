from typing import Any

from app.db.connection import execute_query
from app.db.pagination import execute_paginated_query

SQL_GET_VENDOR = "SELECT * FROM vendor.vendors WHERE vendor_id = :vendor_id"


SQL_GET_RECOMMENDATIONS_BY_REQUEST = """
    SELECT *
    FROM vendor.vendor_recommendations
    WHERE request_id = :request_id
    ORDER BY rank
"""

SQL_GET_HISTORICAL_PERFORMANCE = """
    SELECT *
    FROM vendor.vendor_historical_performance
    WHERE vendor_id = :vendor_id
    ORDER BY period_year DESC, period_month DESC
"""
SQL_GET_VENDOR_BY_NAME = """
    SELECT *
    FROM vendor.vendors
    WHERE vendor_name = :vendor_name
    """

    
#To GET vendors (paginated)
def get_vendors(page: int = 1, page_size: int = 20) -> dict[str, Any]:
    return execute_paginated_query(
        from_clause="vendor.vendors",
        order_by="vendor_id",
        page=page,
        page_size=page_size,
    )

#To GET a vendor by id
def get_vendor(vendor_id : str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_VENDOR, {
        "vendor_id": vendor_id
    })

def get_vendor_by_name(vendor_name: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_VENDOR_BY_NAME, {"vendor_name": vendor_name})

def get_vendors_by_ids(vendors_ids:list[str]) -> list[dict[str, Any]]:
    return execute_query("select * from vendor.vendors where vendor_id = ANY(CAST(:vendors_ids AS uuid[]))",{"vendors_ids": vendors_ids})


#Vendor Products

def get_vendor_products(page:int =1 , page_size:int =20) -> dict[str, Any]:
    return execute_paginated_query(
        from_clause= "vendor.vendor_products",
        order_by= "vendor_product_id",
        page=page,
        page_size=page_size,
    )


#Vendor Recommendations
def get_vendor_recommendations(page:int =1 , page_size:int =20) -> dict[str, Any]:
    return execute_paginated_query(
        from_clause= "vendor.vendor_recommendations",
        order_by= "recommendation_id",
        page=page,
        page_size=page_size,
    )

def get_recommendations_by_request(request_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_RECOMMENDATIONS_BY_REQUEST, {"request_id": request_id})
    

# Vendor Historical Performance
def get_historical_performance(vendor_id: str) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_HISTORICAL_PERFORMANCE, {"vendor_id": vendor_id})
    
#Vendor Categories

def get_vendor_by_category_names(category_names: list[str])->list[dict[str, Any]]:
    return execute_query("select * from vendor.vendor_categories where category_name = ANY(CAST(:category_names AS varchar[]))",{"category_names": category_names})

#vendor production capacity by vendor id
def get_vendor_production_capacity(vendor_id:str)->list[dict[str, Any]]:
    return execute_query("select * from vendor.production_capacity where vendor_id =:vendor_id",{"vendor_id": vendor_id})
