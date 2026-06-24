from fastmcp import FastMCP
from client import post

mcp = FastMCP("chat")


@mcp.tool()
async def chat(message: str, session_id: str = None) -> dict:
    """
    Send a natural language procurement query and get a response.
    Use session_id from a previous response to continue the same conversation.
    Example: 'suggest vendors for Resistors Grade-A, 50 items'
    """
    body = {"message": message}
    if session_id:
        body["session_id"] = session_id
    return await post("/chat", data=body)
