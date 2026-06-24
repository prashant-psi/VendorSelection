import re
from typing import Any

from app.repositories import product_search

PRODUCT_CODE_PATTERN = re.compile(r"PRD-\d+", re.IGNORECASE)


def extract_product_code(text: str) -> str | None:
    match = PRODUCT_CODE_PATTERN.search(text or "")
    return match.group(0).upper() if match else None


def _format_product(match: dict[str, Any]) -> dict[str, str]:
    return {
        "product_id": str(match["product_id"]),
        "product_name": match.get("product_name", ""),
        "product_code": match.get("product_code", ""),
        "category": match.get("category", ""),
    }


def resolve_products(
    product_id: str = "",
    product_name: str = "",
    product_code: str = "",
) -> tuple[list[dict[str, str]], dict[str, Any] | None]:
    """
    Resolve one or more products for ranking.

    Product name is sufficient — if multiple SKUs share the same name, all are included
    and vendors are ranked across them.
    """
    if product_id:
        return [{"product_id": str(product_id), "product_name": "", "product_code": "", "category": ""}], None

    code = (product_code or "").strip() or extract_product_code(product_name) or ""
    if code:
        matches = product_search.get_product_by_code(code)
        if not matches:
            return [], {"error": f"No product found with code '{code}'", "product_code": code}
        return [_format_product(matches[0])], None

    name = (product_name or "").strip()
    if not name:
        return [], {"error": "Please mention the product name (e.g. Resistors Grade-A)"}

    matches = product_search.search_products(name, limit=50)
    if not matches:
        return [], {"error": f"No product found matching '{name}'", "search_term": name}

    return [_format_product(m) for m in matches], None


def resolve_product_id(
    product_id: str = "",
    product_name: str = "",
    product_code: str = "",
) -> tuple[str | None, dict[str, Any] | None]:
    """Resolve a single product id (first match when multiple share a name)."""
    products, error = resolve_products(product_id, product_name, product_code)
    if error:
        return None, error
    if not products:
        return None, {"error": "No product found"}
    return products[0]["product_id"], None


def resolve_vendor_id(vendor_id: str = "", vendor_name: str = "") -> tuple[str | None, dict[str, Any] | None]:
    if vendor_id:
        return str(vendor_id), None

    name = (vendor_name or "").strip()
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
