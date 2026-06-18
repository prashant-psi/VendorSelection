from contextvars import ContextVar
from typing import Any

_tool_names: ContextVar[list[str] | None] = ContextVar("tool_names", default=None)
_tool_result: ContextVar[Any] = ContextVar("tool_result", default=None)


def reset_tool_tracking() -> None:
    _tool_names.set([])
    _tool_result.set(None)


def get_tool_tracking() -> tuple[list[str], Any]:
    return _tool_names.get() or [], _tool_result.get()


def record_tool_result(name: str, result: Any) -> None:
    names = list(_tool_names.get() or [])
    names.append(name)
    _tool_names.set(names)
    _tool_result.set(result)
