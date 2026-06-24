from fastmcp import FastMCP
from client import get, post

mcp = FastMCP("utils")


@mcp.tool()
async def get_countries() -> list[dict]:
    """Get list of all countries available in the system."""
    return await get("/countries")


@mcp.tool()
async def get_weather_logistics_impact(event_types: list[str]) -> dict:
    """Get weather and logistics impact data for given event types (e.g. ['flood', 'storm'])."""
    return await post("/weather-logistics-impact", data={"event_types": event_types})

@mcp.tool()
async def get_compliance_certifications() -> list[dict]:
    """Get all compliance certifications available in the system."""
    return await get("/compliance-certifications")


@mcp.tool()
async def get_vendor_certifications(vendor_id: str) -> list[dict]:
    """Get compliance certifications held by a specific vendor."""
    return await get(f"/compliance-certifications/vendor/{vendor_id}")


@mcp.tool()
async def get_weight_configs() -> list[dict]:
    """Get all scoring weight configurations."""
    return await get("/weight-configs")


@mcp.tool()
async def get_default_weight_config() -> dict:
    """Get the default scoring weight configuration."""
    return await get("/weight-configs/default")


@mcp.tool()
async def get_weight_config(config_id: str) -> dict:
    """Get a specific scoring weight configuration by ID."""
    return await get(f"/weight-configs/{config_id}")
