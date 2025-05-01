from mcp.server import FastMCP

mcp = FastMCP("Hello World")


@mcp.tool()
async def get_stuff():
    print("Called MCP Server...")
    return {"result": "ok"}


if __name__ == "__main__":
    # Initialize and run the server
    print("Started MCP server...")
    mcp.run(transport='stdio')
