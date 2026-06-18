import re
from typing import Any

from app.core.constants import RANKING_KEYWORDS
from app.models.procurement_request import ProcurementRequest

from .resolver import extract_product_code, resolve_products

QUANTITY_PATTERN = re.compile(
    r"(?:quantity|qty|need|require|required|order)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
ITEMS_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:items?|units?|pcs|pieces)\b", re.IGNORECASE)
FOR_QUANTITY_PATTERN = re.compile(r"\bfor\s+(\d+(?:\.\d+)?)\b", re.IGNORECASE)
PRODUCT_NAME_PATTERN = re.compile(
    r"(?:for\s+)?product\s+(.+?)(?:\s+for\s+\d|\s*,|\s*$)",
    re.IGNORECASE,
)
BUDGET_PATTERN = re.compile(
    r"(?:budget|usd|\$)\s*[:\-]?\s*\$?\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
RESULT_LIMIT_PATTERNS = (
    re.compile(r"\b(?:top|best|first|only|limit)\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"\bgive\s+(?:me\s+)?(?:only\s+)?(\d+)\s+vendors?\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s+(?:top|best)\s+vendors?\b", re.IGNORECASE),
)
MAX_RESULT_LIMIT = 50


def wants_vendor_ranking(message: str) -> bool:
    text = (message or "").lower()
    return any(keyword in text for keyword in RANKING_KEYWORDS)


def extract_product_name(message: str) -> str | None:
    match = PRODUCT_NAME_PATTERN.search(message or "")
    return match.group(1).strip() if match else None


def extract_required_quantity(message: str, explicit: str | None = None) -> str | None:
    if explicit and str(explicit).strip():
        return str(explicit).strip()
    text = message or ""
    for pattern in (QUANTITY_PATTERN, ITEMS_PATTERN, FOR_QUANTITY_PATTERN):
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def extract_budget_usd(message: str, explicit: float | None = None) -> float | None:
    if explicit is not None:
        return explicit
    match = BUDGET_PATTERN.search(message or "")
    return float(match.group(1)) if match else None


def extract_result_limit(message: str, explicit: int | None = None) -> int | None:
    if explicit is not None and explicit > 0:
        return min(int(explicit), MAX_RESULT_LIMIT)
    text = message or ""
    for pattern in RESULT_LIMIT_PATTERNS:
        match = pattern.search(text)
        if match:
            return min(int(match.group(1)), MAX_RESULT_LIMIT)
    return None


def build_procurement(fields: dict[str, Any]) -> tuple[ProcurementRequest | None, dict[str, Any] | None]:
    """Build procurement request from LLM-extracted session fields."""
    product_code = fields.get("product_code") or extract_product_code(fields.get("last_message", ""))
    products, product_error = resolve_products(
        product_id=fields.get("product_id") or "",
        product_name=fields.get("product_name") or "",
        product_code=product_code or "",
    )
    if product_error:
        return None, product_error
    if not products:
        return None, {"error": "No product found for the given name or code"}

    quantity = fields.get("required_quantity") or extract_required_quantity(fields.get("last_message", ""))
    if not quantity:
        return None, {"error": "Required quantity is missing", "missing_fields": ["required_quantity"]}

    product_ids = [p["product_id"] for p in products]
    return ProcurementRequest(
        product_id=product_ids[0],
        product_ids=product_ids if len(product_ids) > 1 else None,
        required_quantity=str(quantity),
        required_by_date=fields.get("required_by_date"),
        budget_usd=fields.get("budget_usd"),
        quality_grade=fields.get("quality_grade"),
        preferred_countries=fields.get("preferred_countries"),
        excluded_countries=fields.get("excluded_countries"),
        weight_config_id=fields.get("weight_config_id"),
        ml_blend_weight=fields.get("ml_blend_weight", 0.2),
    ), {"matched_products": products}
