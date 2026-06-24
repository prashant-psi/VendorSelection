from fastmcp import FastMCP
from client import get

mcp = FastMCP("products")


@mcp.tool()
async def get_products_catalog(page: int = 1, page_size: int = 20) -> dict:
    """Get paginated list of all products in the catalog."""
    return await get("/products-catalog", params={"page": page, "page_size": page_size})


@mcp.tool()
async def search_products(search_term: str) -> list[dict]:
    """Search products by name, product code (e.g. PRD-00217), or category."""
    return await get("/products-catalog", params={"search": search_term})


@mcp.tool()
async def get_product_detail(product_id: str) -> dict:
    """Get full details of a single product by its ID."""
    return await get(f"/products-catalog/{product_id}")


@mcp.tool()
async def get_seasonal_demand(product_id: str) -> dict:
    """Get seasonal demand forecast for a specific product."""
    return await get(f"/products-catalog/{product_id}/seasonal-demand")


@mcp.tool()
async def get_product_vendor_features(
    product_id: str,
    required_quantity: str = None,
    budget_usd: float = None,
    required_by_date: str = None,
) -> dict:
    """Get vendor scoring features for a product. Optionally filter by quantity, budget, and delivery date (YYYY-MM-DD)."""
    params = {}
    if required_quantity:
        params["required_quantity"] = required_quantity
    if budget_usd is not None:
        params["budget_usd"] = budget_usd
    if required_by_date:
        params["required_by_date"] = required_by_date
    return await get(f"/products-catalog/{product_id}/vendor-features", params=params)
