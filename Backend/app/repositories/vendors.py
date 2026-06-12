from typing import Any

from app.db.connection import execute_query
from app.db.pagination import execute_paginated_query

SQL_GET_VENDOR = "SELECT * FROM vendor.vendors WHERE vendor_id = :vendor_id"

SQL_GET_VENDOR_BY_LIMIT = "SELECT * FROM vendor.vendors LIMIT :limit"

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

def get_vendors_by_ids(vendors_ids:list[str]) -> list[dict[str, Any]]:
    return execute_query("select * from vendor.vendors where vendor_id = ANY(CAST(:vendors_ids AS uuid[]))",{"vendors_ids": vendors_ids})


def get_vendors_by_limit(limit:int) -> list[dict[str, Any]]:
    return execute_query(SQL_GET_VENDOR_BY_LIMIT,
    {
        "limit": limit
    })


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

    
#Vendor Categories

def categories() -> list[dict[str, Any]]:
    return execute_query("select distinct category_name from vendor.vendor_categories")

def get_vendor_by_category_names(category_names: list[str])->list[dict[str, Any]]:
    return execute_query("select * from vendor.vendor_categories where category_name = ANY(CAST(:category_names AS varchar[]))",{"category_names": category_names})

#vendor production capacity by vendor id
def get_vendor_production_capacity(vendor_id:str)->list[dict[str, Any]]:
    return execute_query("select * from vendor.production_capacity where vendor_id =:vendor_id",{"vendor_id": vendor_id})
