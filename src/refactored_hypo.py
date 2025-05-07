import asyncio
from graph.graph_builder import make_graph, update, mcp_client

async def refactored_hypo():
    async with make_graph(mcp_client) as graph:
        await update("Tell me about this codebase", graph)

if __name__ == "__main__":
    asyncio.run(refactored_hypo())
