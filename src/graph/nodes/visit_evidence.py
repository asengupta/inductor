from typing import Any

from evidence import Evidence, random_evidence
from graph.nodes.state_operations import push, stack
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, BASE_HYPOTHESIS_KEY, RECURSION_STACK_KEY
from hypothesis import random_hypothesis
from induction_node import InferenceNode


def visit_evidence(state: CodeExplorerState) -> dict[str, Any]:
    current = stack(state)[-1]
    print(f"Visiting evidence: {current[0].just_str()}")
    le_stack = stack(state)
    le_stack[-2] = (le_stack[-2][0], le_stack[-2][1] + 1)
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[],
                             base_hypothesis=state[BASE_HYPOTHESIS_KEY],
                             recursion_stack=state[RECURSION_STACK_KEY])
