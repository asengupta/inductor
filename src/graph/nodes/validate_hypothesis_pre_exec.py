from typing import Any

from evidence import Evidence, random_evidence
from graph.nodes.state_operations import stack, push, pop
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, RECURSION_STACK_KEY, BASE_HYPOTHESIS_KEY
from hypothesis import random_hypothesis
from induction_node import InferenceNode


def validate_hypothesis_pre_exec(state: CodeExplorerState) -> dict[str, Any]:
    print("In Validation Hypothesis PRE-EXEC")
    print("==============================")

    # current = stack(state)[-1]
    # Cook up termination condition here
    # if current[1] <= len(current[0].children) - 1:
    #     push(state, (current[0].children[current[1]], 0))

    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[],
                             base_hypothesis=state[BASE_HYPOTHESIS_KEY], recursion_stack=state[RECURSION_STACK_KEY])
