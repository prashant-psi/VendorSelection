import json

from langchain_core.tools import tool

from app.core.constants import PREDICT_ML_BLEND_WEIGHT
from app.services.chat.context import get_chat_context
from app.services.chat.tools._helpers import (
    _build_procurement_for_tool,
    _resolve_product_or_error,
    _save_tool_result,
)
from app.services.scoring import orchestrator as scoring_service


def _require_quantity(required_quantity: str) -> str | None:
    """Return error JSON if quantity is missing, else None."""
    if not required_quantity or not required_quantity.strip() or required_quantity.strip() == "0":
        return json.dumps({
            "error": "required_quantity is missing. Ask the user how many units they need before ranking vendors."
        })
    return None


@tool
def rank_vendors(
    product_name: str = "",
    product_code: str = "",
    product_id: str = "",
    required_quantity: str = "",
) -> str:
    """Rank vendors using rule-engine + ML blend (80% rules, 20% ML). Use when user wants to find the best vendor for a product. Always ask for quantity before calling this tool if not provided. Prefer product_code (e.g. PRD-00217)."""
    qty_err = _require_quantity(required_quantity)
    if qty_err:
        return qty_err

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
    required_quantity: str = "",
) -> str:
    """Predict best vendors using ML-heavy ranking (70% ML). Use when user wants a data-driven ML prediction. Always ask for quantity before calling this tool if not provided. Prefer product_code when available."""
    qty_err = _require_quantity(required_quantity)
    if qty_err:
        return qty_err

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
