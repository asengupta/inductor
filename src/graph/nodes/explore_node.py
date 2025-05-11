from typing import Any

from graph.nodes.types import LLM
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY


def free_explore(tool_llm: LLM):
    def run_agent(state: CodeExplorerState) -> dict[str, Any]:
        print("In Free Exploration Mode")
        print("=============================")
        print(state)
        response = tool_llm.invoke(["""
        You have multiple tools at your disposal to investigate this codebase. Use as many tools at once as needed. 
        """, state[CURRENT_REQUEST_KEY]])
        print(response.content)
        return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                                 messages=[response])

    return run_agent
