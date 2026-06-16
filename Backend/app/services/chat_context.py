from contextvars import ContextVar
from typing import Any

_chat_context: ContextVar[dict[str, Any]] = ContextVar("chat_context", default={})


def set_chat_context(
    product_id: str | None,
    vendor_id: str | None,
    request_id: str | None,
    product_name: str | None = None,
    vendor_name: str | None = None,
    product_code: str | None = None,
    user_message: str | None = None,
) -> None:
    _chat_context.set({
        "product_id": product_id,
        "vendor_id": vendor_id,
        "request_id": request_id,
        "product_name": product_name,
        "vendor_name": vendor_name,
        "product_code": product_code,
        "user_message": user_message,
    })


def get_chat_context() -> dict[str, Any]:
    return _chat_context.get()
