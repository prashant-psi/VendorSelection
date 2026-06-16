import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from langchain_core.tools import tool

from app.models.procurementRequest_model import ProcurementRequestModel
from app.repositories import product_search
from app.services import scoring_service
from app.services.chat_context import get_chat_context
from app.services.product_resolver import resolve_product_id, resolve_vendor_id

_last_tool_result: Any = None
_last_tool_names: list[str] = []


def reset_tool_tracking() -> None:
    global _last_tool_result, _last_tool_names
    _last_tool_result = None
    _last_tool_names = []


def get_tool_tracking() -> tuple[list[str], Any]:
    return _last_tool_names, _last_tool_result


def _save_tool_result(name: str, result: Any) -> str:
    global _last_tool_result, _last_tool_names
    _last_tool_names.append(name)
    _last_tool_result = result
    return json.dumps(_serialize(result), default=str)


def _resolve_product_or_error(
    product_id: str = "",
    product_name: str = "",
    product_code: str = "",
) -> tuple[str | None, str | None]:
    pid, err = resolve_product_id(
        product_id=product_id,
        product_name=product_name,
        product_code=product_code,
    )
    if err:
        return None, json.dumps(err)
    return pid, None


def _resolve_vendor_or_error(vendor_id: str = "", vendor_name: str = "") -> tuple[str | None, str | None]:
    vid, err = resolve_vendor_id(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return None, json.dumps(err)
    return vid, None


def _serialize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, list):
        return [_serialize_row(row) if isinstance(row, dict) else _serialize(row) for row in value]
    if isinstance(value, dict):
        return _serialize_row(value)
    return value


def _serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, val in row.items():
        if isinstance(val, (UUID, Decimal)):
            clean[key] = str(val)
        elif isinstance(val, (datetime, date)):
            clean[key] = val.isoformat()
        else:
            clean[key] = val
    return clean


@tool
def search_products(search_term: str) -> str:
    """Search products by name or product code (e.g. PRD-00217)."""
    if not search_term.strip():
        return json.dumps({"error": "search_term is required"})
    results = product_search.search_products(search_term)
    return _save_tool_result("search_products", _serialize(results))


@tool
def search_vendors(search_term: str) -> str:
    """Search vendors by name or code."""
    if not search_term.strip():
        return json.dumps({"error": "search_term is required"})
    results = product_search.search_vendors(search_term)
    return _save_tool_result("search_vendors", _serialize(results))


@tool
def rank_vendors(
    product_name: str = "",
    product_code: str = "",
    product_id: str = "",
    required_quantity: str = "1",
) -> str:
    """Rank vendors for a product. Prefer product_code (PRD-00217) when user provides it."""
    pid, err = _resolve_product_or_error(
        product_id=product_id,
        product_name=product_name,
        product_code=product_code,
    )
    if err:
        return err
    proc_request = ProcurementRequestModel(
        product_id=pid,
        requried_quanity=required_quantity,
        use_ml=True,
    )
    return _save_tool_result("rank_vendors", scoring_service.rank_vendors(proc_request))


@tool
def predict_vendors(
    product_name: str = "",
    product_code: str = "",
    product_id: str = "",
    required_quantity: str = "1",
) -> str:
    """Predict best vendors using XGBoost. Prefer product_code when user provides it."""
    pid, err = _resolve_product_or_error(
        product_id=product_id,
        product_name=product_name,
        product_code=product_code,
    )
    if err:
        return err
    proc_request = ProcurementRequestModel(
        product_id=pid,
        requried_quanity=required_quantity,
        use_ml=True,
    )
    return _save_tool_result("predict_vendors", scoring_service.predict_vendors(proc_request))


@tool
def get_scoring_features(product_name: str = "", product_code: str = "", product_id: str = "") -> str:
    """Get scoring feature breakdown for a product. Prefer product_code when available."""
    pid, err = _resolve_product_or_error(
        product_id=product_id,
        product_name=product_name,
        product_code=product_code,
    )
    if err:
        return err
    return _save_tool_result("get_scoring_features", scoring_service.get_vendor_features(pid))


@tool
def get_vendor_latest_scores(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get latest aggregated vendor scores."""
    ctx = get_chat_context()
    if vendor_name or vendor_id or ctx.get("vendor_id") or ctx.get("vendor_name"):
        vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
        if err and (vendor_name or vendor_id or ctx.get("vendor_name")):
            return err
        return _save_tool_result("get_vendor_latest_scores", scoring_service.get_vendor_latest_scores(vid))
    return _save_tool_result("get_vendor_latest_scores", scoring_service.get_vendor_latest_scores(None))


@tool
def get_quality_scores(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get quality score history for a vendor."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_quality_scores", scoring_service.get_quality_scores(vid))


@tool
def get_risk_scores(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get risk score history for a vendor."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_risk_scores", scoring_service.get_risk_scores(vid))


@tool
def get_seasonal_demand(product_name: str = "", product_code: str = "", product_id: str = "") -> str:
    """Get demand forecast for a product. Prefer product_code when available."""
    pid, err = _resolve_product_or_error(
        product_id=product_id,
        product_name=product_name,
        product_code=product_code,
    )
    if err:
        return err
    return _save_tool_result("get_seasonal_demand", scoring_service.get_seasonal_demand(pid))


@tool
def get_recommendations(request_id: str = "") -> str:
    """Get stored recommendations for a procurement request."""
    ctx = get_chat_context()
    rid = request_id or ctx.get("request_id")
    if not rid:
        return json.dumps({"error": "request_id is required"})
    return _save_tool_result("get_recommendations", scoring_service.get_recommendations_by_request(rid))


@tool
def get_historical_performance(vendor_name: str = "", vendor_id: str = "") -> str:
    """Get monthly historical performance for a vendor."""
    vid, err = _resolve_vendor_or_error(vendor_id=vendor_id, vendor_name=vendor_name)
    if err:
        return err
    return _save_tool_result("get_historical_performance", scoring_service.get_historical_performance(vid))


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
