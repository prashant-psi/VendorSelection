from fastapi import APIRouter

from app.models.vendor_model import VendorByCategoryNamesRequestModel, VendorDetailsRequestModel
from app.api.pagination import PaginationDep
from app.services import vendor_service

router = APIRouter()


@router.get("/vendors")
def list_vendors(pagination: PaginationDep):
    return vendor_service.get_vendors(
        page=pagination.page,
        page_size=pagination.page_size,
    )

@router.get("/vendors/{vendor_id}")
def get_vendor(vendor_id: str):
    return vendor_service.get_vendor(vendor_id)

@router.post("/vendors/ids")
def get_vendors_by_ids(requestBody: VendorDetailsRequestModel):
    return vendor_service.get_vendors_by_ids(requestBody.vendor_ids)

@router.get("/vendors/limit/{limit}")
def get_vendors_by_limit(limit:int):
    return vendor_service.get_vendors_by_limit(limit)


# Vendor Products
@router.get("/vendor-products")
def get_vendor_products(pagination: PaginationDep):
    return vendor_service.get_vendor_products(
        page = pagination.page,
        page_size = pagination.page_size,
    )

# Vendor Recommendations
@router.get("/vendor-recommendations")
def get_vendor_recommendations(pagination: PaginationDep):
    return vendor_service.get_vendor_recommendations(
        page = pagination.page,
        page_size = pagination.page_size,
    )
# Vendor Categories

@router.get("/categories")
def get_categories():
    return vendor_service.get_categories()

@router.post("/vendor-by-category")
def get_vendor_categoey_by_vendors(requestBody: VendorByCategoryNamesRequestModel):
    return vendor_service.get_vendor_by_category_names(requestBody.category_names)

# Vendor Production Capacity
@router.get("/vendor-production-capacity/{vendor_id}")
def get_vendor_production_capacity(vendor_id: str):
    return vendor_service.get_vendor_production_capacity(vendor_id)