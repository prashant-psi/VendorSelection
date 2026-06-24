from fastmcp import FastMCP
from tools.vendor import mcp as vendors_mcp
from tools.product import mcp as products_mcp
from tools.utils import mcp as utils_mcp
from tools.users import mcp as users_mcp
from tools.ranking import mcp as ranking_mcp
from tools.chat import mcp as chat_mcp

mcp = FastMCP("VendorSelection")

mcp.mount("vendors", vendors_mcp)
mcp.mount("products", products_mcp)
mcp.mount("utils", utils_mcp)
mcp.mount("users", users_mcp)
mcp.mount("ranking", ranking_mcp)
mcp.mount("chat", chat_mcp)

if __name__ == "__main__":
    mcp.run()
    # For external clients switch to:
    # mcp.run(transport="sse", host="0.0.0.0", port=8001)
