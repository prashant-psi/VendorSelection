from typing import Any, TypedDict


class Permissions(TypedDict):
    read_only: bool
    allowed_operations: list[str]


class ChatState(TypedDict):
    session_id: str
    message: str
    previous_fields: dict[str, Any]
    extracted: dict[str, Any]
    merged_fields: dict[str, Any]
    missing_fields: list[str]
    should_rank: bool
    response: Any
    permissions: Permissions
