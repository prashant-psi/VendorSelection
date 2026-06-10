from typing import Any

from app.repositories import vendors

#Vendors Details

def get_vendors(page: int = 1, page_size: int = 20) -> dict[str, Any]:
    return vendors.get_vendors(page=page, page_size=page_size)

def get_vendor(vendor_id : str) -> list[dict[str, Any]]:
    return vendors.get_vendor(vendor_id)

def get_vendors_by_limit(limit:int) -> list[dict[str, Any]]:
    return vendors.get_vendors_by_limit(limit)


#vendor products

def get_vendor_products(page:int=1, page_size:int=20) -> dict[str, Any]:
    return vendors.get_vendor_products(page=page, page_size=page_size)

#Vendor Recommendations

def get_vendor_recommendations(page:int=1, page_size:int=20) -> dict[str, Any]:
    return vendors.get_vendor_recommendations(page=page, page_size=page_size)

#Vendor Categories
def get_vendor_categories(page:int =1 , page_size:int =20) -> dict[str, Any]:
    return vendors.get_vendor_categories(page=page, page_size=page_size)