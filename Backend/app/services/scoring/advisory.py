from typing import Any

from app.repositories.vendor_scoring_data import (
    fetch_all_product_vendors,
    fetch_vendors_with_partial_capacity,
)


def build_quantity_advisory(
    product_id: str,
    required_quantity: float,
    ranked_vendors: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Find vendors excluded due to capacity < required_quantity and suggest splits.
    Returns None if every vendor can fully fulfill the order.
    """
    try:
        qty = float(required_quantity)
    except (TypeError, ValueError):
        return None

    partial = fetch_vendors_with_partial_capacity(product_id, qty)
    if not partial:
        return None

    partial_list = [
        {
            "vendor_id": str(row["vendor_id"]),
            "vendor_name": row["vendor_name"],
            "max_order_qty": int(row["max_order_qty"]),
            "shortfall": int(qty - row["max_order_qty"]),
            "unit_price": float(row["unit_price"]) if row.get("unit_price") else None,
            "lead_time_days": row.get("lead_time_days"),
        }
        for row in partial
    ]

    splits = _suggest_splits(partial_list, ranked_vendors, qty)

    return {
        "required_quantity": int(qty),
        "partial_vendors": partial_list,
        "split_suggestions": splits,
        "message": _build_advisory_message(partial_list, splits, int(qty)),
    }


def build_filter_advisory(
    product_id: str,
    required_quantity: float | None,
    max_lead_days: int | None,
) -> dict[str, Any] | None:
    """
    Called when 0 vendors pass procurement filters.
    Fetches all vendors for the product without filters, diagnoses why each
    was excluded, and suggests what to change to unlock vendors.
    Returns None if no vendors exist at all for this product.
    """
    all_vendors = fetch_all_product_vendors(product_id)
    if not all_vendors:
        return None

    vendor_reports = []
    for v in all_vendors:
        min_qty = _safe_int(v.get("min_order_qty"))
        max_qty = _safe_int(v.get("max_order_qty"))
        lead_time = _safe_int(v.get("lead_time_days"))

        qty_ok = True
        lead_ok = True
        issues: list[str] = []
        suggestions: list[str] = []

        if required_quantity is not None:
            if min_qty is not None and min_qty > required_quantity:
                qty_ok = False
                issues.append(
                    f"requires min {min_qty} units (you requested {int(required_quantity)})"
                )
                suggestions.append(f"increase order to at least {min_qty} units")
            if max_qty is not None and max_qty < required_quantity:
                qty_ok = False
                issues.append(
                    f"can supply max {max_qty} units (you need {int(required_quantity)})"
                )
                suggestions.append(f"reduce quantity or split order (max available: {max_qty})")

        if max_lead_days is not None and lead_time is not None and lead_time > max_lead_days:
            lead_ok = False
            issues.append(
                f"delivers in {lead_time} days (you need within {max_lead_days} days)"
            )
            suggestions.append(f"extend deadline to {lead_time}+ days")

        vendor_reports.append({
            "vendor_id": str(v["vendor_id"]),
            "vendor_name": v["vendor_name"],
            "min_order_qty": min_qty,
            "max_order_qty": max_qty,
            "lead_time_days": lead_time,
            "unit_price": float(v["unit_price"]) if v.get("unit_price") else None,
            "qty_ok": qty_ok,
            "lead_ok": lead_ok,
            "issues": issues,
            "suggestions": suggestions,
        })

    return {
        "type": "filter_advisory",
        "required_quantity": int(required_quantity) if required_quantity is not None else None,
        "max_lead_days": max_lead_days,
        "vendors": vendor_reports,
        "message": _build_filter_advisory_message(
            vendor_reports, required_quantity, max_lead_days
        ),
    }


def _build_filter_advisory_message(
    vendor_reports: list[dict],
    required_quantity: float | None,
    max_lead_days: int | None,
) -> str:
    lines = ["No vendors matched your exact requirements. Here is what is available:"]
    lines.append("")

    for v in vendor_reports:
        lead = f"{v['lead_time_days']} days" if v["lead_time_days"] is not None else "unknown lead time"
        min_q = str(v["min_order_qty"]) if v["min_order_qty"] is not None else "—"
        max_q = str(v["max_order_qty"]) if v["max_order_qty"] is not None else "—"

        if v["qty_ok"] and not v["lead_ok"]:
            status = f"quantity OK, but delivers in {lead} (you need within {max_lead_days} days)"
        elif not v["qty_ok"] and v["lead_ok"]:
            status = f"lead time OK ({lead}), but quantity constraint — range: {min_q}–{max_q}"
        else:
            status = " | ".join(v["issues"]) if v["issues"] else "excluded by multiple filters"

        lines.append(f"  • {v['vendor_name']}: {status}")

    unique_suggestions: list[str] = []
    for v in vendor_reports:
        for s in v["suggestions"]:
            if s not in unique_suggestions:
                unique_suggestions.append(s)

    if unique_suggestions:
        lines.append("")
        lines.append("To unlock vendors, consider:")
        for s in unique_suggestions[:4]:
            lines.append(f"  → {s}")

    return "\n".join(lines)


def _suggest_splits(
    partial_vendors: list[dict],
    ranked_vendors: list[dict],
    required_qty: float,
) -> list[dict[str, Any]]:
    """Greedy split: pair each partial vendor with the top ranked vendor to fill the gap."""
    suggestions = []

    for partial in partial_vendors[:3]:
        partial_qty = partial["max_order_qty"]
        remaining = int(required_qty - partial_qty)

        if remaining <= 0:
            continue

        fill_vendor = ranked_vendors[0] if ranked_vendors else None
        if not fill_vendor:
            continue

        suggestions.append({
            "vendors": [
                {
                    "vendor_name": partial["vendor_name"],
                    "qty": partial_qty,
                    "note": f"supplies up to their max of {partial_qty}",
                },
                {
                    "vendor_name": fill_vendor.get("vendor_name", "Top ranked vendor"),
                    "qty": remaining,
                    "note": f"supplies the remaining {remaining}",
                },
            ],
            "total_qty": int(required_qty),
        })

    return suggestions


def _build_advisory_message(
    partial_vendors: list[dict],
    splits: list[dict],
    required_qty: int,
) -> str:
    lines = [
        f"Some vendors cannot supply the full quantity of {required_qty} units but can partially fulfill your order:"
    ]
    for v in partial_vendors:
        lines.append(
            f"  • {v['vendor_name']} — can supply up to {v['max_order_qty']} units "
            f"(shortfall: {v['shortfall']} units)"
        )

    if splits:
        lines.append("\nSplit order suggestions to meet your full requirement:")
        for i, split in enumerate(splits, 1):
            parts = " + ".join(
                f"{s['qty']} units from {s['vendor_name']}" for s in split["vendors"]
            )
            lines.append(f"  Option {i}: {parts}")

    return "\n".join(lines)


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None
