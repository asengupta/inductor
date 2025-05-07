from typing import Any, Dict

from graph.state import MyState

def validate_hypothesis(state: MyState) -> Dict[str, Any]:
    print("In validating hypothesis")
    print("=====================")
    print(state)
    message = "Validation of hypothesis not yet implemented"
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"] + [message])
