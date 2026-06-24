from fastmcp import FastMCP
from client import get

mcp = FastMCP("users")


@mcp.tool()
async def get_users(page: int = 1, page_size: int = 20) -> dict:
    """Get paginated list of all users in the system."""
    return await get("/users", params={"page": page, "page_size": page_size})


@mcp.tool()
async def get_user(user_id: str) -> dict:
    """Get details of a specific user by their ID."""
    return await get(f"/users/{user_id}")
