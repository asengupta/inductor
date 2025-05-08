from typing import Any, Dict

from graph.state import MyState

def free_explore(tool_llm):
    def run_agent(state: MyState) -> Dict[str, Any]:
        print("In Free Exploration Mode")
        print("=============================")
        print(state)
        response = tool_llm.invoke(["""
        You have multiple tools at your disposal to investigate this codebase. Use as many tools at once as needed. 
        """, state["current_request"]])
        print(response.content)
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=[response])

    return run_agent
