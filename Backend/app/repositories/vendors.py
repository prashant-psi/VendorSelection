from typing import Any
from unicodedata import category

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

def get_vendor_categories(page:int =1 , page_size:int =20) -> dict[str, Any]:
    return execute_paginated_query(
        from_clause="vendor.vendor_categories",
        order_by="category_id",
        page=page,
        page_size=page_size,
    )


