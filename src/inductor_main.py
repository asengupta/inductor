import asyncio
from graph.graph_builder import make_graph, start_task_graph, mcp_client


async def run_inductor():
    async with make_graph(mcp_client) as graph:
        await start_task_graph("Tell me about this codebase", graph)


if __name__ == "__main__":
    asyncio.run(run_inductor())
