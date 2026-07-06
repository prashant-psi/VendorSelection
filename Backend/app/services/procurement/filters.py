from datetime import date, datetime
from typing import Any


_DATE_FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y")


def parse_quantity(value: str | float | int | None) -> float | None:
    """Parse a quantity value to float; returns None if missing or non-positive."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = float(text)
        return parsed if parsed > 0 else None
    except ValueError:
        return None


def days_until_delivery(required_by_date: str | None) -> int | None:
    """Convert a delivery date string to number of days from today; returns None if blank/unparseable."""
    if not required_by_date or not str(required_by_date).strip():
        return None
    target: date | None = None
    for fmt in _DATE_FORMATS:
        try:
            target = datetime.strptime(required_by_date.strip(), fmt).date()
            break
        except ValueError:
            continue
    if target is None:
        return None
    return max((target - date.today()).days, 0)


def build_procurement_sql_filters(
    *,
    required_quantity: str | float | int | None = None,
    budget_usd: float | None = None,
    required_by_date: str | None = None,
) -> dict[str, Any]:
    """
    Convert high-level procurement fields into raw SQL filter parameters
    ready to be passed to vendor_scoring_data.fetch_eligible_vendor_products().
    """
    quantity = parse_quantity(required_quantity)
    return {
        "min_qty": quantity,
        "max_qty": quantity,
        "required_quantity": quantity,
        "budget": budget_usd,
        "max_lead_days": days_until_delivery(required_by_date),
    }
