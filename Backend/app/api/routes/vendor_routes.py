from fastapi import APIRouter

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

@router.get("/vendor-categories")
def get_vendor_categories(pagination: PaginationDep):
    return vendor_service.get_vendor_categories(
        page = pagination.page,
        page_size = pagination.page_size,
    )