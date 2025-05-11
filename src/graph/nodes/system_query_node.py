from typing import Any

from graph.nodes.types import LLM
from graph.state import CodeExplorerState


def system_query(tool_llm: LLM, tools):
    def run_agent(state: CodeExplorerState) -> dict[str, Any]:
        print("In System Query Mode")
        print("=============================")
        print(state)
        response = tool_llm.invoke([
            f"The list of Model Context Protocol tools are: {tools}. Answer the following request without using any tools: {state["current_request"]}"])
        print(response.content)
        return CodeExplorerState(input=state["input"], current_request=state["current_request"],
                                 messages=state["messages"] + [response])

    return run_agent
