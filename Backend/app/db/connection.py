import re
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result

from app.config import vendor_connection_url

engine = create_engine(
    vendor_connection_url,
    pool_pre_ping=True,
)

_FIRST_KEYWORD = re.compile(r"^\s*(\w+)", re.IGNORECASE)

# Only these SQL statement types are allowed through execute_query
_ALLOWED_KEYWORDS = frozenset({"select", "with", "explain"})


def _assert_read_only(sql: str) -> None:
    """Raise PermissionError if the SQL is not a read-only statement."""
    match = _FIRST_KEYWORD.match(sql)
    if not match:
        raise PermissionError("Empty or unparseable SQL statement rejected.")
    keyword = match.group(1).lower()
    if keyword not in _ALLOWED_KEYWORDS:
        raise PermissionError(
            f"Write operation '{keyword.upper()}' is not permitted. "
            "Only SELECT queries are allowed through this connection."
        )


def execute_query(sql_query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run a parameterized read-only query and return rows as dicts.
    Raises PermissionError if the SQL is anything other than SELECT / WITH / EXPLAIN."""
    _assert_read_only(sql_query)
    with engine.connect() as conn:
        result: Result = conn.execute(text(sql_query), params or {})
        return [dict(row) for row in result.mappings().all()]
