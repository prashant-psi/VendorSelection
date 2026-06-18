"""JSON-safe serialization for API responses."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


def serialize_response(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, list):
        return [_serialize_row(row) if isinstance(row, dict) else serialize_response(row) for row in value]
    if isinstance(value, dict):
        return _serialize_row(value)
    return value


def _serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, val in row.items():
        if isinstance(val, (UUID, Decimal)):
            clean[key] = str(val)
        elif isinstance(val, (datetime, date)):
            clean[key] = val.isoformat()
        else:
            clean[key] = val
    return clean
