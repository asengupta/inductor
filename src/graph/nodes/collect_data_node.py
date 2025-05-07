from typing import Any, Dict
from langchain_core.messages import BaseMessage

from graph.state import MyState

def collect_data_for_hypothesis(tool_llm):
    def run_agent(state: MyState) -> Dict[str, Any]:
        print("============IN COLLECT DATA TO BUILD HYPOTHESIS===============")
        msg = """
        You have multiple tools to investigate the codebase. Use as many of them as needed to get some initial
        info about the codebase. This info will be ultimately used to hypothesize about the large-scale purpose
        of the codebase and the small-scale purpose of its various sections.
        """
        messages = state["messages"]
        print(f"Asking explorer to: {msg}")
        response = tool_llm.invoke(msg)
        print(response.content)
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"] + [response], llm_response=response)

    return run_agent
