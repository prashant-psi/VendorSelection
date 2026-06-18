from typing import Any


def to_float(value: Any) -> float:
    """Coerce DB/JSON values to float; None and missing become 0.0."""
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return float(value)
    return float(value)
