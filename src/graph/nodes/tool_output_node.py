from typing import Any, Callable

from graph.nodes.types import LanggraphNode
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY


def as_str(state: CodeExplorerState) -> str:
    return str(state)


def generic_tool_output(tool_name: str, formatter: Callable[[CodeExplorerState], str] = as_str) -> LanggraphNode:
    def show_output(state: CodeExplorerState) -> dict[str, Any]:
        print(f"In tool_output of {tool_name}...")
        print("=====================")
        # print(formatter(state[MESSAGES_KEY]))
        print(formatter(state))
        return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                                 messages=state[MESSAGES_KEY])

    return show_output
