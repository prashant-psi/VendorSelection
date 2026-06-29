import json

from langchain_core.tools import tool

from app.core.serialization import serialize_response
from app.repositories import product_search
from app.services import utils_service, vendor_service
from app.services.chat.tools._helpers import (
    _resolve_vendor_or_error,
    _save_tool_result,
)


@tool
def search_vendors(search_term: str) -> str:
    """Search vendors by name or vendor code. Use when user asks about a vendor by name."""
    if not search_term.strip():
        return json.dumps({"error": "search_term is required"})
    return _save_tool_result("search_vendors", serialize_response(product_search.search_vendors(search_term)))


@tool
def get_vendor_details(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get full profile of a single vendor — contact, country, tier, trade name. Use when user asks for vendor details."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_vendor_details", vendor_service.get_vendor(vid))


@tool
def get_vendor_latest_scores(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get latest aggregated scores for a vendor. Omit both to get scores for all vendors."""
    from app.services.chat.context import get_chat_context
    ctx = get_chat_context()
    if vendor_name or vendor_id or ctx.get("vendor_id") or ctx.get("vendor_name"):
        vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
        if err and (vendor_name or vendor_id or ctx.get("vendor_name")):
            return err
        return _save_tool_result("get_vendor_latest_scores", vendor_service.get_vendor_latest_scores(vid))
    return _save_tool_result("get_vendor_latest_scores", vendor_service.get_vendor_latest_scores(None))


@tool
def get_quality_scores(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get quality score history for a vendor. Use when user asks about quality performance over time."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_quality_scores", vendor_service.get_quality_scores(vid))


@tool
def get_risk_scores(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get risk score history for a vendor. Use when user asks about vendor reliability or risk."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_risk_scores", vendor_service.get_risk_scores(vid))


@tool
def get_historical_performance(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get monthly historical performance metrics for a vendor — OTD, CSAT, defect rate, etc."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_historical_performance", vendor_service.get_historical_performance(vid))


@tool
def get_vendor_production_capacity(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get production capacity details for a vendor — max output, lead time, min order qty."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_vendor_production_capacity", vendor_service.get_vendor_production_capacity(vid))


@tool
def get_vendors_by_category(category_names: list[str]) -> str:
    """Get all vendors that supply a given list of product categories."""
    if not category_names:
        return json.dumps({"error": "category_names is required"})
    return _save_tool_result("get_vendors_by_category", vendor_service.get_vendor_by_category_names(category_names))


@tool
def get_categories() -> str:
    """Get all product categories available in the system. Use when user asks what categories or types of products are available."""
    return _save_tool_result("get_categories", vendor_service.get_categories())


@tool
def get_vendor_certifications(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get compliance certifications held by a vendor — ISO, quality, safety certs."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_vendor_certifications", utils_service.get_certification_by_vendorId(vid))
