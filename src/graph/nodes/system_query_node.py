from typing import Any

from graph.nodes.types import LLM
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY


def system_query(tool_llm: LLM, tools):
    def run_agent(state: CodeExplorerState) -> dict[str, Any]:
        print("In System Query Mode")
        print("=============================")
        print(state)
        response = tool_llm.invoke([
            f"The list of Model Context Protocol tools are: {tools}. Answer the following request without using any tools: {state[CURRENT_REQUEST_KEY]}"])
        print(response.content)
        return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                                 messages=state[MESSAGES_KEY] + [response])

    return run_agent
