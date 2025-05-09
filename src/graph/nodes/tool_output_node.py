from typing import Any, Dict, Callable

from langchain_core.messages import BaseMessage

from graph.state import MyState


def as_str(state: MyState) -> str:
    return str(state)


def generic_tool_output(tool_name: str, formatter: Callable[[MyState], str] = as_str):
    def show_output(state: MyState) -> Dict[str, Any]:
        print(f"In tool_output of {tool_name}...")
        print("=====================")
        # print(formatter(state["messages"]))
        print(formatter(state))
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"])

    return show_output
