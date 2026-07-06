from typing import Any

from app.db.connection import execute_query


def get_product_by_code(product_code: str) -> list[dict[str, Any]]:
    """Exact match on product_code (e.g. PRD-00217)."""
    return execute_query(
        """
        SELECT product_id, product_code, product_name, category, sub_category
        FROM vendor.products_catalog
        WHERE is_active = true
          AND UPPER(product_code) = UPPER(:product_code)
        """,
        {"product_code": product_code.strip()},
    )


def search_products(search_term: str, limit: int = 10) -> list[dict[str, Any]]:
    """Find products by name, code, or category (case-insensitive fuzzy search)."""
    term = search_term.strip()
    pattern = f"%{term}%"
    return execute_query(
        """
        SELECT product_id, product_code, product_name, category, sub_category
        FROM vendor.products_catalog
        WHERE is_active = true
          AND (
            product_name ILIKE :pattern
            OR product_code ILIKE :pattern
            OR category ILIKE :pattern
            OR search_keywords ILIKE :pattern
          )
        ORDER BY product_name, product_code
        LIMIT :limit
        """,
        {"pattern": pattern, "limit": limit},
    )


def search_vendors(search_term: str, limit: int = 10) -> list[dict[str, Any]]:
    """Find vendors by name or code (case-insensitive)."""
    pattern = f"%{search_term.strip()}%"
    return execute_query(
        """
        SELECT vendor_id, vendor_code, vendor_name, country_code, tier
        FROM vendor.vendors
        WHERE is_active = true
          AND blacklist_flag = false
          AND (
            vendor_name ILIKE :pattern
            OR vendor_code ILIKE :pattern
            OR trade_name ILIKE :pattern
          )
        ORDER BY vendor_name
        LIMIT :limit
        """,
        {"pattern": pattern, "limit": limit},
    )


def get_product_by_id(product_id: str) -> list[dict[str, Any]]:
    return execute_query(
        """
        SELECT product_id, product_code, product_name, category
        FROM vendor.products_catalog
        WHERE product_id = :product_id
        """,
        {"product_id": product_id},
    )
