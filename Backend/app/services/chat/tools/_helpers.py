import json
from typing import Any

from app.core.serialization import serialize_response
from app.core.constants import PREDICT_ML_BLEND_WEIGHT
from app.services.chat.context import get_chat_context
from app.services.chat.tool_tracker import record_tool_result
from app.services.procurement.builder import build_procurement, extract_budget_usd, extract_required_quantity
from app.services.procurement.resolver import resolve_product_id, resolve_vendor_id


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


def _resolve_vendor_or_error(
    vendor_id: str = "",
    vendor_name: str = "",
) -> tuple[str | None, str | None]:
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
    required_quantity: str = "",
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
