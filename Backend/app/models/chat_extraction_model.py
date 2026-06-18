from typing import Literal

from pydantic import BaseModel, Field


class LlmExtractedFields(BaseModel):
    """Fields the LLM extracts from natural language (internal)."""

    intent: Literal[
        "vendor_ranking",
        "vendor_prediction",
        "general_question",
        "vendor_scores",
        "product_info",
        "unknown",
    ] = "unknown"
    run_ranking: bool = False
    product_name: str | None = None
    required_quantity: str | None = None
    product_code: str | None = None
    result_limit: int | None = Field(None, description="Number of top vendors to return e.g. 5 or 10")
    budget_usd: float | None = None
    required_by_date: str | None = None
    quality_grade: str | None = None
    preferred_countries: list[str] | None = None
    excluded_countries: list[str] | None = None
    follow_up_question: str | None = None
