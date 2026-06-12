from pydantic import BaseModel, Field

class WeatherLogisticsImpactRequestModel(BaseModel):
    event_types: list[str] = Field(..., description="List of event types", min_length=1, max_length=100)