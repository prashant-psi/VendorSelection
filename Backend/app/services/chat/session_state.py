"""Per-session procurement fields extracted from conversation."""

import re
from typing import Any

_CODE_RE = re.compile(r"PRD-\d+", re.IGNORECASE)

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

    new_name = (new_fields.get("product_name") or "").strip()
    new_code = (new_fields.get("product_code") or "").strip()
    msg = (new_fields.get("last_message") or "")

    # Use raw message as source of truth — LLMs sometimes echo old values even
    # when the user didn't type them in the current message.
    code_in_message = bool(_CODE_RE.search(msg))
    name_in_message = bool(new_name and new_name.lower() in msg.lower())

    if name_in_message and not code_in_message:
        # User explicitly typed a product name with no code → name-only search,
        # clear any stale code regardless of whether the name changed.
        current.pop("product_code", None)
        current.pop("product_id", None)
    elif code_in_message and not name_in_message:
        # User explicitly typed a code with no product name → code-only search,
        # clear any stale name.
        current.pop("product_name", None)
        current.pop("product_id", None)
    # both in message → keep both (loop sets the new values)
    # neither in message → keep existing product fields unchanged

    for key in _FIELD_KEYS:
        value = new_fields.get(key)
        if value is not None and value != "" and value != []:
            current[key] = value
    _session_store[session_id] = current
    return dict(current)
