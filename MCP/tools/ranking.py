from fastmcp import FastMCP
from client import get, post

mcp = FastMCP("ranking")


@mcp.tool()
async def get_model_status() -> dict:
    """Get the current XGBoost model status, version, and training metadata."""
    return await get("/model/status")


@mcp.tool()
async def train_model() -> dict:
    """Trigger XGBoost model retraining on latest vendor data."""
    return await post("/model/train", data={})


@mcp.tool()
async def rank_vendors(
    product_id: str,
    required_quantity: str,
    required_by_date: str = None,
    budget_usd: float = None,
    quality_grade: str = None,
    preferred_countries: list[str] = None,
    excluded_countries: list[str] = None,
    weight_config_id: str = None,
    ml_blend_weight: float = 0.2,
) -> dict:
    """Rank vendors for a product using rule-engine + ML blend (default 80% rules, 20% ML)."""
    body = {
        "product_id": product_id,
        "required_quantity": required_quantity,
        "ml_blend_weight": ml_blend_weight,
    }
    if required_by_date:
        body["required_by_date"] = required_by_date
    if budget_usd is not None:
        body["budget_usd"] = budget_usd
    if quality_grade:
        body["quality_grade"] = quality_grade
    if preferred_countries:
        body["preferred_countries"] = preferred_countries
    if excluded_countries:
        body["excluded_countries"] = excluded_countries
    if weight_config_id:
        body["weight_config_id"] = weight_config_id
    return await post("/rank", data=body)


@mcp.tool()
async def predict_vendors(
    product_id: str,
    required_quantity: str,
    required_by_date: str = None,
    budget_usd: float = None,
    quality_grade: str = None,
    preferred_countries: list[str] = None,
    excluded_countries: list[str] = None,
    weight_config_id: str = None,
    ml_blend_weight: float = 0.7,
) -> dict:
    """Predict best vendors using ML-heavy ranking (default 70% ML, 30% rules)."""
    body = {
        "product_id": product_id,
        "required_quantity": required_quantity,
        "ml_blend_weight": ml_blend_weight,
    }
    if required_by_date:
        body["required_by_date"] = required_by_date
    if budget_usd is not None:
        body["budget_usd"] = budget_usd
    if quality_grade:
        body["quality_grade"] = quality_grade
    if preferred_countries:
        body["preferred_countries"] = preferred_countries
    if excluded_countries:
        body["excluded_countries"] = excluded_countries
    if weight_config_id:
        body["weight_config_id"] = weight_config_id
    return await post("/predict", data=body)
