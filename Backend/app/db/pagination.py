from typing import Any

from app.db.connection import execute_query


def paginated_response(*, items: list[dict[str, Any]], page: int, page_size: int, total: int) -> dict[str, Any]:
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }


def execute_paginated_query(*,from_clause: str, order_by: str, page: int = 1, page_size: int = 20, params: dict[str, Any] | None = None) -> dict[str, Any]:  
    """
    Run a paginated read for any table or filtered subquery.

    from_clause and order_by must come from application code (never user input).
    Example from_clause values:
      - "vendor.vendors"
      - "vendor.vendors WHERE is_active = :is_active"
    """
    query_params = dict(params or {})
    offset = (page - 1) * page_size

    count_sql = f"SELECT COUNT(*) AS total FROM {from_clause}"
    
    list_sql = f""" SELECT * FROM {from_clause}
                    ORDER BY {order_by}
                    LIMIT :limit OFFSET :offset
                """

    total = execute_query(count_sql, query_params)[0]["total"]
    items = execute_query(
        list_sql,
        {**query_params, "limit": page_size, "offset": offset},
    )
    return paginated_response(
        items,
        page=page,
        page_size=page_size,
        total=total,
    )
