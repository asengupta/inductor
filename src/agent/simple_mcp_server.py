from mcp.server import FastMCP

mcp = FastMCP("Hello World")


@mcp.tool()
async def say_hello(name: str):
    print("Called MCP Server...")
    return {"result": f"Hi hello! {name}"}


if __name__ == "__main__":
    # Initialize and run the server
    print("Started MCP server...")
    mcp.run(transport='stdio')
