from fastapi import APIRouter

from app.api.pagination import PaginationDep
from app.models.vendor_model import VendorByCategoryNamesRequestModel, VendorDetailsRequestModel
from app.services import vendor_service

router = APIRouter(tags=["vendors"])


@router.get("/vendors")
def list_vendors(pagination: PaginationDep):
    return vendor_service.get_vendors(page=pagination.page, page_size=pagination.page_size)

@router.get("/vendor/{vendor_name}")
def get_vendor_by_name(vendor_name: str):
    return vendor_service.get_vendor_by_name(vendor_name)


@router.post("/vendors/ids")
def get_vendors_by_ids(requestBody: VendorDetailsRequestModel):
    return vendor_service.get_vendors_by_ids(requestBody.vendor_ids)


@router.get("/vendors/{vendor_id}")
def get_vendor(vendor_id: str):
    return vendor_service.get_vendor(vendor_id)


@router.get("/vendors/{vendor_id}/quality-scores")
def get_quality_scores(vendor_id: str):
    return vendor_service.get_quality_scores(vendor_id)


@router.get("/vendors/{vendor_id}/risk-scores")
def get_risk_scores(vendor_id: str):
    return vendor_service.get_risk_scores(vendor_id)


@router.get("/vendors/{vendor_id}/historical-performance")
def get_historical_performance(vendor_id: str):
    return vendor_service.get_historical_performance(vendor_id)


@router.get("/vendor-products")
def get_vendor_products(pagination: PaginationDep):
    return vendor_service.get_vendor_products(page=pagination.page, page_size=pagination.page_size)


@router.get("/vendor-recommendations")
def get_vendor_recommendations(pagination: PaginationDep):
    return vendor_service.get_vendor_recommendations(page=pagination.page, page_size=pagination.page_size)


@router.get("/vendor-recommendations/by-request/{request_id}")
def get_recommendations_by_request(request_id: str):
    return vendor_service.get_recommendations_by_request(request_id)

@router.post("/vendor-by-category")
def get_vendor_categoey_by_vendors(requestBody: VendorByCategoryNamesRequestModel):
    return vendor_service.get_vendor_by_category_names(requestBody.category_names)


@router.get("/vendor-production-capacity/{vendor_id}")
def get_vendor_production_capacity(vendor_id: str):
    return vendor_service.get_vendor_production_capacity(vendor_id)
