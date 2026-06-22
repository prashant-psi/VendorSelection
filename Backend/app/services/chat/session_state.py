"""Per-session procurement fields extracted from conversation."""

from typing import Any

_session_store: dict[str, dict[str, Any]] = {}

_FIELD_KEYS = (
    "product_id",
    "product_name",
    "product_code",
    "required_quantity",
    "required_by_date",
    "budget_usd",
    "quality_grade",
    "preferred_countries",
    "excluded_countries",
    "weight_config_id",
    "ml_blend_weight",
    "result_limit",
    "ranking_in_progress",
    "last_message",
)


def get_session_fields(session_id: str) -> dict[str, Any]:
    return dict(_session_store.get(session_id, {}))


def merge_session_fields(session_id: str, new_fields: dict[str, Any]) -> dict[str, Any]:
    current = _session_store.get(session_id, {})
    new_code = new_fields.get("product_code")
    if new_code and new_code != current.get("product_code"):
        current.pop("product_id", None)
    for key in _FIELD_KEYS:
        value = new_fields.get(key)
        if value is not None and value != "" and value != []:
            current[key] = value
    _session_store[session_id] = current
    return dict(current)
