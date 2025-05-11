from typing import Any

from evidence import Evidence, random_evidence
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, INFERENCE_STACK_KEY
from graph.tool_names import BASE_HYPOTHESIS_KEY
from hypothesis import Hypothesis, random_hypothesis
from induction_node import InferenceNode


def validate_hypothesis(state: CodeExplorerState) -> dict[str, Any]:
    print("In Validation Hypothesis")
    print("==============================")
    print("Not doing anything yet, just showing the base hypothesis")
    # root_hypothesis: InferenceNode = state[BASE_HYPOTHESIS_KEY]
    root_hypothesis = InferenceNode(random_hypothesis(),
                                    [InferenceNode(random_hypothesis(),
                                                   [
                                                       InferenceNode(random_evidence()),
                                                       InferenceNode(random_evidence())
                                                   ]),
                                     InferenceNode(random_hypothesis(),
                                                   [
                                                       InferenceNode(random_evidence()),
                                                       InferenceNode(random_evidence())
                                                   ])
                                     ])
    print(root_hypothesis.as_tree())

    recurse([root_hypothesis])
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[],
                             base_hypothesis=root_hypothesis)


def gather_evidence_with_tool(stack) -> None:
    print(f"Visiting evidence: {stack[-1].just_str()}")


def recurse(stack: list[InferenceNode]) -> None:
    current = stack[-1]
    if isinstance(current.node, Evidence):
        gather_evidence_with_tool(stack)
        return
    visit_hypothesis(stack)


def visit_hypothesis(stack):
    current = stack[-1]
    print(f"Visiting hypothesis: {current.just_str()}")
    stack.append(current)
    for child in current.children:
        stack.append(child)
        recurse(stack)
        stack.pop()
    stack.pop()
