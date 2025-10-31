import asyncio
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from src.taskgraph.models import anthropic_model, ollama_model


# Define a simple state model for our workflow
class WorkflowState(BaseModel):
    messages: List[Any] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)


# Create MCP client for cmd_line_mcp
cmd_line_mcp_client = MultiServerMCPClient(
    {
        "cmd_line_mcp": {
            "command": "/Users/asgupta/code/cmd-line-mcp/venv/bin/cmd-line-mcp",
            "args": ["--config", "/Users/asgupta/code/cmd-line-mcp/bash_mcp_config.json"],
            "transport": "stdio",
        }
    }
)


# Function to call the MCP server via a ReAct agent
async def call_mcp_server(state: WorkflowState) -> WorkflowState:
    """Node that calls the cmd_line_mcp server using a ReAct agent."""
    # Get tools from the MCP server
    tools = await cmd_line_mcp_client.get_tools()

    # base_llm = anthropic_model()
    base_llm = ollama_model()
    # Create a ReAct agent with the tools
    agent = create_react_agent(
        model=base_llm,
        tools=tools,
    )

    # Create a prompt for the agent
    prompt = """
    You are a helpful assistant with access to tools.
    Use the tools available to you to help the user accomplish their tasks.
    List the contents of the current directory. Do not qualify the results with any extra information.
    """

    # Invoke the agent with the prompt
    # response = await agent.ainvoke({
    #     "messages": [
    #         {"role": "user", "content": prompt}
    #     ]
    # })
    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    # Update state with the agent's response
    state.results["agent_response"] = response
    state.messages.append(HumanMessage(content=f"ReAct agent response: {response}"))

    return state


# Create and run the workflow
async def create_workflow():
    # Create the workflow
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("call_mcp", call_mcp_server)

    # Add edges
    workflow.add_edge(START, "call_mcp")
    workflow.add_edge("call_mcp", END)

    # Compile the workflow
    return workflow.compile()


async def run_workflow():
    # Create the workflow
    graph = await create_workflow()

    # Run the workflow
    result = await graph.ainvoke({"messages": [HumanMessage(content="Starting workflow")]})

    print("Workflow completed!")
    print(f"Results: {result['results']}")

    # Print messages in a more readable format
    print("\nMessages:")
    for i, message in enumerate(result['messages']):
        print(f"\n--- Message {i + 1} ---")
        if hasattr(message, 'content'):
            if isinstance(message.content, str):
                print(message.content)
            else:
                print(f"Complex content: {message.content}")
        else:
            print(f"Message without content attribute: {message}")


if __name__ == "__main__":
    asyncio.run(run_workflow())
