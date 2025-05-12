import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

async def run():
    async with MultiServerMCPClient(
            {
                "getStuff": {
                    "command": "python",
                    "args": ["/Users/asgupta/code/inductor-langgraph-mcp/src/src/agent/simple_mcp_server.py"],
                    "transport": "stdio",
                }
            }
    ) as client:
        agent = create_react_agent(
            "anthropic:claude-3-5-sonnet-20241022",
            client.get_tools()
        )

        stuff_response = await agent.ainvoke({"messages":
                                                  ["You have tools, use them.",
                                                   HumanMessage(content="Get me stuff")]})
        print("RESPONSE: {}".format(stuff_response))

load_dotenv("./env/.env")
asyncio.run(run())
