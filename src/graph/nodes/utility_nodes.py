from typing import Any, Dict

from graph.state import MyState

def executive_init(state: MyState) -> Dict[str, Any]:
    print("In step 1")
    print(state)
    user_input: str = input("What do you want to do? ")
    print(state)

    return MyState(input=user_input, current_request=user_input, messages=state["messages"])


def fallback(state: MyState) -> Dict[str, Any]:
    print("THIS IS A FALLBACK NODE, GOING BACK TO ROOT==============")
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"])


def step_4(state: MyState) -> Dict[str, Any]:
    print("In step 4")
    print(state)
    return {"step_4_state": "DONE"}
