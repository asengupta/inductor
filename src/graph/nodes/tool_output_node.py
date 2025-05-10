from typing import Any, Dict, Callable

from langchain_core.messages import BaseMessage

from graph.state import CodeExplorerState


def as_str(state: CodeExplorerState) -> str:
    return str(state)


def generic_tool_output(tool_name: str, formatter: Callable[[CodeExplorerState], str] = as_str):
    def show_output(state: CodeExplorerState) -> Dict[str, Any]:
        print(f"In tool_output of {tool_name}...")
        print("=====================")
        # print(formatter(state["messages"]))
        print(formatter(state))
        return CodeExplorerState(input=state["input"], current_request=state["current_request"],
                                 messages=state["messages"])

    return show_output
