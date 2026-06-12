from typing import Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result
from app.config import vendor_connection_url

engine = create_engine(
    vendor_connection_url,
    pool_pre_ping=True,
)


def execute_query(sql_query: str,params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run a parameterized read query and return rows as dicts."""
    with engine.connect() as conn:
        result: Result = conn.execute(text(sql_query), params or {})
        return [dict(row) for row in result.mappings().all()]
