from typing import Any

from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, MESSAGES_KEY, INPUT_KEY


def executive_init(state: CodeExplorerState) -> dict[str, Any]:
    print("In step 1")
    print(state)
    user_input: str = input("What do you want to do? ")
    print(state)

    return CodeExplorerState(input=user_input, current_request=user_input, messages=state[MESSAGES_KEY])


def fallback(state: CodeExplorerState) -> dict[str, Any]:
    print("THIS IS A FALLBACK NODE, GOING BACK TO ROOT==============")
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY])


def step_4(state: CodeExplorerState) -> dict[str, Any]:
    print("In step 4")
    print(state)
    return {"step_4_state": "DONE"}
