from typing import Any


def apply_result_limit(ranking: dict[str, Any], limit: int | None) -> dict[str, Any]:
    """Trim rankings to the user-requested count and re-number ranks."""
    rankings = ranking.get("rankings") or []
    if not limit or limit <= 0:
        return ranking

    limited = [dict(vendor) for vendor in rankings[:limit]]
    for index, vendor in enumerate(limited, start=1):
        vendor["rank"] = index

    return {
        **ranking,
        "rankings": limited,
        "result_limit": limit,
        "total_ranked": len(rankings),
    }
