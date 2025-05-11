from typing import Any

from evidence import Evidence
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, INFERENCE_STACK_KEY
from graph.tool_names import BASE_HYPOTHESIS_KEY
from induction_node import InferenceNode


def validate_hypothesis(state: CodeExplorerState) -> dict[str, Any]:
    print("In Validation Hypothesis")
    print("==============================")
    print("Not doing anything yet, just showing the base hypothesis")
    root_hypothesis: InferenceNode = state[BASE_HYPOTHESIS_KEY]
    print(root_hypothesis.as_tree())

    stack = [root_hypothesis]

    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=state[INFERENCE_STACK_KEY],
                             base_hypothesis=root_hypothesis)


def gather_evidence_with_tool(stack) -> None:
    stack[-1].node


def recurse(stack: list[InferenceNode]) -> CodeExplorerState:
    current = stack[-1]
    if isinstance(current.node, Evidence):
        gather_evidence_with_tool(stack)
    for child in current.children:
        stack.append(child)
        recurse(stack)
