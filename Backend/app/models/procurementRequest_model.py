from pydantic import BaseModel, Field

class ProcurementRequestModel(BaseModel):
    product_id: str = Field(..., description="Product ID")
    requried_quanity:str  = Field(..., description="Required Quantity")
    required_by_date:str|None = Field(None, description="Required Date")
    budget_usd:float|None = Field(None, description="Budget in USD")
    quality_grade:str|None = Field(None, description="Quality Grade")
    preferred_countries:list[str]|None = Field(None, description="Preferred Countries")
    excluded_countries:list[str]|None = Field(None, description="Excluded Countries")
    weight_config_id:str|None = Field(None, description="Scoring weight configuration ID")
    use_ml:bool = Field(True, description="Use XGBoost model when available")