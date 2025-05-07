from typing import Any, Dict

from graph.state import MyState

def generic_tool_output(tool_name: str):
    def show_output(state: MyState) -> Dict[str, Any]:
        print(f"In tool_output of {tool_name}...")
        print("=====================")
        print(state)
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"])

    return show_output
