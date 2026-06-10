from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result


DEFAULT_DATABASE_URL = (
    "postgresql+psycopg2://postgres:postgres@ps-win-ds-288:5432/VendorPlatform"
)
engine = create_engine(
    DEFAULT_DATABASE_URL
)


def execute_query(sql_query: str,params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run a parameterized read query and return rows as dicts."""
    with engine.connect() as conn:
        result: Result = conn.execute(text(sql_query), params or {})
        return [dict(row) for row in result.mappings().all()]
