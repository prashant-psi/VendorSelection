from pydantic import AliasChoices, BaseModel, Field


class ProcurementRequest(BaseModel):
    product_id: str = Field(..., description="Primary product ID used for ranking")
    product_ids: list[str] | None = Field(
        None,
        description="All product IDs when multiple SKUs match the same name",
    )
    required_quantity: str = Field(
        ...,
        description="Required order quantity",
        validation_alias=AliasChoices("required_quantity", "requried_quanity"),
    )
    required_by_date: str | None = Field(None, description="Required delivery date")
    budget_usd: float | None = Field(None, description="Budget cap in USD")
    quality_grade: str | None = Field(None, description="Minimum acceptable quality grade")
    preferred_countries: list[str] | None = Field(None, description="Preferred vendor countries")
    excluded_countries: list[str] | None = Field(None, description="Excluded vendor countries")
    weight_config_id: str | None = Field(None, description="Scoring weight configuration ID")
    ml_blend_weight: float | None = Field(
        0.2,
        description="ML share in final score (0=rules only, 1=ML only)",
    )
