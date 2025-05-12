import asyncio

from src.taskgraph.graph_builder import make_graph, mcp_client


async def run_inductor():
    async with make_graph(mcp_client) as graph:
        print(graph.get_graph().draw_mermaid())


if __name__ == "__main__":
    asyncio.run(run_inductor())
