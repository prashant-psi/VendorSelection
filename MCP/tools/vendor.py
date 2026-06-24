from fastmcp import FastMCP
from client import get


mcp = FastMCP("vendors")

@mcp.tool()
async def get_all_vendors(page:int =1 ,page_size:int =20 ) ->dict:
    return await get("/vendors",params={"page": page, "page_size": page_size})

@mcp.tool()
async def get_vendor_by_ids(vendors_ids:list[str]) -> list[dict]:
    return await post("/vendors/ids",data={"vendors_ids": vendors_ids})

@mcp.tool()
async def get_quality_scores(vendor_id:str) -> list[dict]:
    return await get(f"/vendors/{vendor_id}/quality-scores")

@mcp.tool()
async def get_risk_scores(vendor_id:str) -> list[dict]:
    return await get(f"/vendors/{vendor_id}/risk-scores")

@mcp.tool()
async def get_historical_performance(vendor_id:str) -> list[dict]:
    return await get(f"/vendors/{vendor_id}/historical-performance")

@mcp.tool()
async def get_vendor_products(page:int =1 ,page_size:int =20 ) ->dict:
    return await get("/vendor-products",params={"page": page, "page_size": page_size})

@mcp.tool()
async def get_vendor_recommendations(page:int =1 ,page_size:int =20 ) ->dict:
    return await get("/vendor-recommendations",params={"page": page, "page_size": page_size})

@mcp.tool()
async def get_recommendations_by_request(request_id:str) -> list[dict]:
    return await get(f"/vendor-recommendations/by-request/{request_id}")

@mcp.tool()
async def get_categories() -> list[dict]:
    return await get("/categories")

@mcp.tool()
async def get_vendor_categoey_by_vendors(category_names:list[str]) -> list[dict]:
    return await post("/vendor-by-category",data={"category_names": category_names})

@mcp.tool()
async def get_vendor_production_capacity(vendor_id:str) -> list[dict]:
    return await get(f"/vendor-production-capacity/{vendor_id}")