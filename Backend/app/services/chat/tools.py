import json
from typing import Any

from langchain_core.tools import tool

from app.core.constants import PREDICT_ML_BLEND_WEIGHT
from app.core.serialization import serialize_response
from app.repositories import product_search
from app.services.chat.context import get_chat_context
from app.services.chat.tool_tracker import record_tool_result
from app.services.procurement.builder import build_procurement, extract_budget_usd, extract_required_quantity
from app.services.procurement.resolver import resolve_product_id, resolve_vendor_id
from app.services import utils_service, vendor_service
from app.services.scoring import orchestrator as scoring_service


def _save_tool_result(name: str, result: Any) -> str:
    record_tool_result(name, result)
    return json.dumps(serialize_response(result), default=str)


def _resolve_product_or_error(
    product_id: str = "",
    product_name: str = "",
    product_code: str = "",
) -> tuple[str | None, str | None]:
    ctx = get_chat_context()
    pid, err = resolve_product_id(
        product_id=product_id or str(ctx.get("product_id") or ""),
        product_name=product_name or str(ctx.get("product_name") or ""),
        product_code=product_code or str(ctx.get("product_code") or ""),
    )
    if err:
        return None, json.dumps(err)
    return pid, None


def _resolve_vendor_or_error(vendor_id: str = "", vendor_name: str = "") -> tuple[str | None, str | None]:
    ctx = get_chat_context()
    vid, err = resolve_vendor_id(
        vendor_id=vendor_id or str(ctx.get("vendor_id") or ""),
        vendor_name=vendor_name or str(ctx.get("vendor_name") or ""),
    )
    if err:
        return None, json.dumps(err)
    return vid, None


def _build_procurement_for_tool(
    product_id: str,
    required_quantity: str = "1",
    ml_blend_weight: float | None = 0.2,
) -> tuple[Any, str | None]:
    ctx = get_chat_context()
    fields = {
        "product_id": product_id,
        "required_quantity": required_quantity,
        "ml_blend_weight": ml_blend_weight,
        "last_message": ctx.get("user_message") or "",
    }
    procurement, meta = build_procurement(fields)
    if not procurement:
        return None, json.dumps(meta or {"error": "Could not build procurement request"})
    return procurement, None


@tool
def search_products(search_term: str) -> str:
    """Search products by name or product code (e.g. PRD-00217)."""
    if not search_term.strip():
        return json.dumps({"error": "search_term is required"})
    return _save_tool_result("search_products", serialize_response(product_search.search_products(search_term)))


@tool
def search_vendors(search_term: str) -> str:
    """Search vendors by name or code."""
    if not search_term.strip():
        return json.dumps({"error": "search_term is required"})
    return _save_tool_result("search_vendors", serialize_response(product_search.search_vendors(search_term)))


@tool
def rank_vendors(
    product_name: str = "",
    product_code: str = "",
    product_id: str = "",
    required_quantity: str = "1",
) -> str:
    """Rank vendors using merged rule-engine + ML score. Prefer product_code (PRD-00217)."""
    ctx = get_chat_context()
    pid, err = _resolve_product_or_error(
        product_id=product_id or str(ctx.get("product_id") or ""),
        product_name=product_name or str(ctx.get("product_name") or ""),
        product_code=product_code or str(ctx.get("product_code") or ""),
    )
    if err:
        return err

    procurement, build_err = _build_procurement_for_tool(str(pid), required_quantity)
    if build_err:
        return build_err

    return _save_tool_result("rank_vendors", scoring_service.rank_vendors(procurement))


@tool
def predict_vendors(
    product_name: str = "",
    product_code: str = "",
    product_id: str = "",
    required_quantity: str = "1",
) -> str:
    """Predict vendors with ML-heavy merged ranking (70% ML). Prefer product_code when available."""
    ctx = get_chat_context()
    pid, err = _resolve_product_or_error(
        product_id=product_id or str(ctx.get("product_id") or ""),
        product_name=product_name or str(ctx.get("product_name") or ""),
        product_code=product_code or str(ctx.get("product_code") or ""),
    )
    if err:
        return err

    procurement, build_err = _build_procurement_for_tool(
        str(pid), required_quantity, ml_blend_weight=PREDICT_ML_BLEND_WEIGHT
    )
    if build_err:
        return build_err

    return _save_tool_result("predict_vendors", scoring_service.predict_vendors(procurement))


def _vendor_filter_kwargs_from_tool(
    required_quantity: str = "",
    budget_usd: float | None = None,
    required_by_date: str = "",
) -> dict[str, Any]:
    ctx = get_chat_context()
    message = str(ctx.get("user_message") or "")
    qty = required_quantity.strip() or extract_required_quantity(message) or "1"
    budget = budget_usd if budget_usd is not None else extract_budget_usd(message)
    delivery_date = required_by_date.strip() or None
    return {
        "required_quantity": qty,
        "budget_usd": budget,
        "required_by_date": delivery_date,
    }


@tool
def get_scoring_features(
    product_name: str = "",
    product_code: str = "",
    product_id: str = "",
    required_quantity: str = "",
    budget_usd: float | None = None,
    required_by_date: str = "",
) -> str:
    """Get scoring feature breakdown for a product. Prefer product_code when available."""
    pid, err = _resolve_product_or_error(product_id=product_id, product_name=product_name, product_code=product_code)
    if err:
        return err
    filters = _vendor_filter_kwargs_from_tool(
        required_quantity=required_quantity,
        budget_usd=budget_usd,
        required_by_date=required_by_date,
    )
    return _save_tool_result(
        "get_scoring_features",
        utils_service.get_product_vendor_features(pid, **filters),
    )


@tool
def get_vendor_latest_scores(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get latest aggregated vendor scores."""
    ctx = get_chat_context()
    if vendor_name or vendor_id or ctx.get("vendor_id") or ctx.get("vendor_name"):
        vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
        if err and (vendor_name or vendor_id or ctx.get("vendor_name")):
            return err
        return _save_tool_result("get_vendor_latest_scores", vendor_service.get_vendor_latest_scores(vid))
    return _save_tool_result("get_vendor_latest_scores", vendor_service.get_vendor_latest_scores(None))


@tool
def get_quality_scores(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get quality score history for a vendor."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_quality_scores", vendor_service.get_quality_scores(vid))


@tool
def get_risk_scores(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get risk score history for a vendor."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_risk_scores", vendor_service.get_risk_scores(vid))


@tool
def get_seasonal_demand(product_name: str = "", product_code: str = "", product_id: str = "") -> str:
    """Get demand forecast for a product. Prefer product_code when available."""
    pid, err = _resolve_product_or_error(product_id=product_id, product_name=product_name, product_code=product_code)
    if err:
        return err
    return _save_tool_result("get_seasonal_demand", utils_service.get_seasonal_demand(pid))


@tool
def get_recommendations(request_id: str = "") -> str:
    """Get stored recommendations for a procurement request."""
    ctx = get_chat_context()
    rid = request_id or ctx.get("request_id")
    if not rid:
        return json.dumps({"error": "request_id is required"})
    return _save_tool_result("get_recommendations", vendor_service.get_recommendations_by_request(rid))


@tool
def get_historical_performance(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get monthly historical performance for a vendor."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_historical_performance", vendor_service.get_historical_performance(vid))


CHAT_TOOLS = [
    search_products,
    search_vendors,
    rank_vendors,
    predict_vendors,
    get_scoring_features,
    get_vendor_latest_scores,
    get_quality_scores,
    get_risk_scores,
    get_seasonal_demand,
    get_recommendations,
    get_historical_performance,
]
