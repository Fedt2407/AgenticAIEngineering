from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("date_server")

@mcp.tool()
async def get_current_date() -> str:
    """Get the current date and time as a string."""
    return datetime.now().isoformat()

if __name__ == "__main__":
    mcp.run(transport='stdio')
