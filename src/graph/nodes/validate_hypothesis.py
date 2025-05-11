from typing import Any

from evidence import Evidence, random_evidence
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY
from hypothesis import random_hypothesis
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

    state["recursion_stack"] = [root_hypothesis]
    recurse(state)
    print(f"At the end: stack = {stack(state)}")
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[],
                             base_hypothesis=root_hypothesis)


def stack(state: CodeExplorerState) -> list[InferenceNode]:
    return state["recursion_stack"]


def push(state, node: InferenceNode) -> None:
    state["recursion_stack"].append(node)


def pop(state) -> InferenceNode:
    return state["recursion_stack"].pop()


def gather_evidence_with_tool(state: CodeExplorerState) -> None:
    print(f"Visiting evidence: {stack(state)[-1].just_str()}")


def recurse(state: CodeExplorerState) -> None:
    current = stack(state)[-1]
    if isinstance(current.node, Evidence):
        gather_evidence_with_tool(state)
        return
    visit_hypothesis(state)


def visit_hypothesis(state: CodeExplorerState) -> None:
    current = stack(state)[-1]
    print(f"Visiting hypothesis: {current.just_str()}")
    push(state, current)
    for child in current.children:
        push(state, child)
        recurse(state)
        pop(state)
    pop(state)
