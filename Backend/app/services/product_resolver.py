import re
from typing import Any

from app.repositories import product_search
from app.services.chat_context import get_chat_context

# Matches product codes like PRD-00217 in user messages
PRODUCT_CODE_PATTERN = re.compile(r"PRD-\d+", re.IGNORECASE)


def extract_product_code(text: str) -> str | None:
    """Pull product code from text, e.g. 'PRD-00217' from the user message."""
    match = PRODUCT_CODE_PATTERN.search(text or "")
    return match.group(0).upper() if match else None


def resolve_product_id(
    product_id: str = "",
    product_name: str = "",
    product_code: str = "",
) -> tuple[str | None, dict[str, Any] | None]:
    """
    Resolve a product to its UUID.

    Priority:
      1. product_id (UUID)
      2. product_code (PRD-00217) — unique in database
      3. product_name search
    """
    ctx = get_chat_context()

    if product_id:
        return str(product_id), None

    if ctx.get("product_id"):
        return str(ctx["product_id"]), None

    code = (product_code or ctx.get("product_code") or "").strip()
    if not code:
        code = extract_product_code(product_name) or extract_product_code(ctx.get("user_message", "")) or ""

    if code:
        matches = product_search.get_product_by_code(code)
        if matches:
            return str(matches[0]["product_id"]), None
        return None, {"error": f"No product found with code '{code}'", "product_code": code}

    name = (product_name or ctx.get("product_name") or "").strip()
    if not name:
        return None, {
            "error": "Please mention the product name or code, e.g. 'Rank vendors for Resistors Grade-A (PRD-00217)'"
        }

    matches = product_search.search_products(name, limit=10)
    if not matches:
        return None, {"error": f"No product found matching '{name}'", "search_term": name}

    if len(matches) == 1:
        return str(matches[0]["product_id"]), None

    return None, {
        "error": f"Multiple products match '{name}'. Please provide the product code (e.g. PRD-00217).",
        "matches": [
            {
                "product_id": str(m["product_id"]),
                "product_name": m["product_name"],
                "product_code": m.get("product_code"),
                "category": m.get("category"),
            }
            for m in matches
        ],
    }


def resolve_vendor_id(vendor_id: str = "", vendor_name: str = "", vendor_code: str = "") -> tuple[str | None, dict[str, Any] | None]:
    """Resolve vendor by id, code, or name."""
    ctx = get_chat_context()

    if vendor_id:
        return str(vendor_id), None

    if ctx.get("vendor_id"):
        return str(ctx["vendor_id"]), None

    name = (vendor_name or ctx.get("vendor_name") or "").strip()
    if not name:
        return None, {"error": "Please mention the vendor name"}

    matches = product_search.search_vendors(name, limit=10)
    if not matches:
        return None, {"error": f"No vendor found matching '{name}'", "search_term": name}

    if len(matches) == 1:
        return str(matches[0]["vendor_id"]), None

    return None, {
        "error": f"Multiple vendors match '{name}'. Please be more specific.",
        "matches": [
            {
                "vendor_id": str(m["vendor_id"]),
                "vendor_name": m["vendor_name"],
                "vendor_code": m.get("vendor_code"),
                "country_code": m.get("country_code"),
            }
            for m in matches
        ],
    }
