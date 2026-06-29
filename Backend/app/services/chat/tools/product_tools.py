import json

from langchain_core.tools import tool

from app.core.serialization import serialize_response
from app.repositories import product_search
from app.services import utils_service
from app.services.chat.tools._helpers import (
    _resolve_product_or_error,
    _save_tool_result,
    _vendor_filter_kwargs_from_tool,
)


@tool
def search_products(search_term: str) -> str:
    """Search products by name or product code (e.g. PRD-00217). Use to look up a product when user mentions it by name."""
    if not search_term.strip():
        return json.dumps({"error": "search_term is required"})
    return _save_tool_result("search_products", serialize_response(product_search.search_products(search_term)))


@tool
def get_product_detail(
    product_name: str = "",
    product_code: str = "",
    product_id: str = "",
) -> str:
    """Get full details of a single product — category, sub-category, specifications. Prefer product_code when available."""
    pid, err = _resolve_product_or_error(product_id=product_id, product_name=product_name, product_code=product_code)
    if err:
        return err
    return _save_tool_result("get_product_detail", utils_service.get_product_detail(pid))


@tool
def get_seasonal_demand(
    product_name: str = "",
    product_code: str = "",
    product_id: str = "",
) -> str:
    """Get seasonal demand forecast for a product. Use when user asks about demand trends or best time to procure."""
    pid, err = _resolve_product_or_error(product_id=product_id, product_name=product_name, product_code=product_code)
    if err:
        return err
    return _save_tool_result("get_seasonal_demand", utils_service.get_seasonal_demand(pid))


@tool
def get_scoring_features(
    product_name: str = "",
    product_code: str = "",
    product_id: str = "",
    required_quantity: str = "",
    budget_usd: float | None = None,
    required_by_date: str = "",
) -> str:
    """Get raw vendor scoring feature breakdown for a product — MOQ, price, lead time per vendor. Prefer product_code when available."""
    pid, err = _resolve_product_or_error(product_id=product_id, product_name=product_name, product_code=product_code)
    if err:
        return err
    filters = _vendor_filter_kwargs_from_tool(
        required_quantity=required_quantity,
        budget_usd=budget_usd,
        required_by_date=required_by_date,
    )
    return _save_tool_result("get_scoring_features", utils_service.get_product_vendor_features(pid, **filters))
