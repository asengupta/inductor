from typing import Any

from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY


def collect_data_for_hypothesis(tool_llm):
    def run_agent(state: CodeExplorerState) -> dict[str, Any]:
        print("============IN COLLECT DATA TO BUILD HYPOTHESIS===============")
        msg = """
        You have multiple tools to investigate the codebase. Use as many of them as needed to get some initial
        info about the codebase. This info will be ultimately used to hypothesize about the large-scale purpose
        of the codebase and the small-scale purpose of its various sections.
        """
        messages = state[MESSAGES_KEY]
        print(f"Asking explorer to: {msg}")
        response = tool_llm.invoke(msg)
        print(response.content)
        return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                                 messages=state[MESSAGES_KEY] + [response], llm_response=response)

    return run_agent
