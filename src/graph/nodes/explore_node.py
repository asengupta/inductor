from typing import Any

from graph.nodes.types import LLM
from graph.state import CodeExplorerState


def free_explore(tool_llm: LLM):
    def run_agent(state: CodeExplorerState) -> dict[str, Any]:
        print("In Free Exploration Mode")
        print("=============================")
        print(state)
        response = tool_llm.invoke(["""
        You have multiple tools at your disposal to investigate this codebase. Use as many tools at once as needed. 
        """, state["current_request"]])
        print(response.content)
        return CodeExplorerState(input=state["input"], current_request=state["current_request"],
                                 messages=[response])

    return run_agent
