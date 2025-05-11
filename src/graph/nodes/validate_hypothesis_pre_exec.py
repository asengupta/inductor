from typing import Any

from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, RECURSION_STACK_KEY, BASE_HYPOTHESIS_KEY


def validate_hypothesis_pre_exec(state: CodeExplorerState) -> dict[str, Any]:
    print("In Validation Hypothesis PRE-EXEC")
    print("==============================")

    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[],
                             base_hypothesis=state[BASE_HYPOTHESIS_KEY], recursion_stack=state[RECURSION_STACK_KEY])
