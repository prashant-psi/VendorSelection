"""Per-session procurement fields extracted from conversation."""

from typing import Any

_session_store: dict[str, dict[str, Any]] = {}

_FIELD_KEYS = (
    "intent",
    "run_ranking",
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
    "last_message",
)


def get_session_fields(session_id: str) -> dict[str, Any]:
    return dict(_session_store.get(session_id, {}))


def merge_session_fields(session_id: str, new_fields: dict[str, Any]) -> dict[str, Any]:
    current = _session_store.get(session_id, {})
    for key in _FIELD_KEYS:
        value = new_fields.get(key)
        if value is not None and value != "" and value != []:
            current[key] = value
    _session_store[session_id] = current
    return dict(current)
