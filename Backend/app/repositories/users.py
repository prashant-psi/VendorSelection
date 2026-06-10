from typing import Any

from app.db.connection import execute_query
from app.db.pagination import execute_paginated_query

def get_users(page:int =1 , page_size:int =20) -> dict[str, Any]:
    return execute_paginated_query(
        from_clause="vendor.users",
        order_by="user_id",
        page=page,
        page_size=page_size,
    )

def get_user(user_id: str) -> list[dict[str, Any]]:
    return execute_query(
        "SELECT * FROM vendor.users WHERE user_id = :user_id",
        {"user_id": user_id},
    )