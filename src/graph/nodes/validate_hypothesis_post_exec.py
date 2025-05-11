from typing import Any

from evidence import Evidence
from graph.nodes.state_operations import stack, push, pop
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, RECURSION_STACK_KEY, BASE_HYPOTHESIS_KEY
from hypothesis import Hypothesis
from induction_node import InferenceNode


def post_visit(le_stack: list[tuple[InferenceNode, int]], tip: tuple[InferenceNode, int]):
    print(f"Post visit: {tip[0].just_str()}")
    le_stack[-2] = (le_stack[-2][0], le_stack[-2][1] + 1)


def pre_visit(le_stack: list[tuple[InferenceNode, int]], tip: tuple[InferenceNode, int]):
    print(f"Pre visit: {tip[0].just_str()}")


def pop_recursive(state):
    le_stack = stack(state)
    pop(le_stack)  # Pop Evidence
    while len(le_stack) > 1 and le_stack[-2][0].children.index(le_stack[-1][0]) == len(le_stack[-2][0].children) - 1:
        post_visit(le_stack, le_stack[-1])
        pop(state)


def validate_hypothesis_post_exec(state: CodeExplorerState) -> dict[str, Any]:
    print("In Validation Hypothesis POST-EXEC")
    print("=====================================")

    le_stack = stack(state)

    current = le_stack[-1]
    parent = le_stack[-2]

    # Terminal condition
    if isinstance(current[0], Evidence) and parent[1] == len(parent[0].children) - 1:
        pop_recursive(state)
        processed_with_incomplete_parent = le_stack.pop()  # Pull out remaining child which has also been completed but it still has more siblings to process
        post_visit(le_stack, processed_with_incomplete_parent)  # Let it do its post-visit
        next_index = le_stack[-1][0].children.index(processed_with_incomplete_parent[0]) + 1
        push(state, (le_stack[-1][0].children[next_index], next_index))  # Push its sibling onto stack for processing
    elif isinstance(current[0], Evidence) and parent[1] < len(parent[0].children) - 1:
        pop(state)
        current_evidence_index = parent[0].children.index(current[0])
        push(state, (parent[0].children[current_evidence_index], 0))
    elif isinstance(current[0], Hypothesis):
        pre_visit(le_stack, current)
        push(state, (current[0].children[0], 0))

    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[],
                             base_hypothesis=state[BASE_HYPOTHESIS_KEY], recursion_stack=state[RECURSION_STACK_KEY])
