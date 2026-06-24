from typing import Any
from app.models.chat_model import ChatResponseModel
from app.services.chat.context import set_chat_context
from app.services.chat.ranking_limit import apply_result_limit
from app.services.chat.tool_tracker import reset_tool_tracking
from app.services.procurement.builder import build_procurement
from app.services.procurement.resolver import extract_product_code
from app.services.scoring import orchestrator as scoring_service
from app.core.serialization import serialize_response

def rank_vendors(fields: dict[str, Any], session_id: str, message: str) -> ChatResponseModel | None:
    product_code = fields.get("product_code") or extract_product_code(message)
    set_chat_context(
        fields.get("product_id"),
        None,
        None,
        product_name=fields.get("product_name"),
        product_code=product_code,
        user_message=message,
    )
    reset_tool_tracking()

    procurement, meta = build_procurement(fields)
    if not procurement:
        error = meta or {"error": "Could not prepare your request."}
        return ChatResponseModel(
            reply=str(error.get("error", "Could not prepare your request.")),
            session_id=session_id,
            data=error,
            actions=["procurement_build_failed"],
        )

    ranking = scoring_service.rank_vendors(procurement)
    if meta and meta.get("matched_products"):
        ranking["matched_products"] = meta["matched_products"]

    limit = fields.get("result_limit")
    if limit:
        ranking = apply_result_limit(ranking, int(limit))

    rankings = ranking.get("rankings") or []
    if not rankings:
        reply = "No vendors found for this product."
    else:
        matched = (meta or {}).get("matched_products") or ranking.get("matched_products") or []
        sku_note = f" across {len(matched)} SKUs" if len(matched) > 1 else ""
        reply = f"Found {len(rankings)} vendor(s){sku_note}. See data for details."

    return ChatResponseModel(
        reply=reply,
        session_id=session_id,
        data=serialize_response(ranking),
        actions=["merged_vendor_ranking"],
    )

