from typing import Any

from evidence import Evidence
from graph.nodes.state_operations import stack, push, pop, print_stack
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, RECURSION_STACK_KEY, BASE_HYPOTHESIS_KEY
from hypothesis import Hypothesis
from induction_node import InferenceNode


def post_visit(le_stack: list[tuple[InferenceNode, int]], tip: tuple[InferenceNode, int]):
    print(f"Post visit Hypothesis: {tip[0].just_str()}")
    if len(le_stack) > 1:
        print(f"Updating count of {le_stack[-2][0].just_str()} by 1...")
        le_stack[-2] = (le_stack[-2][0], le_stack[-2][1] + 1)


def pre_visit(le_stack: list[tuple[InferenceNode, int]], tip: tuple[InferenceNode, int]):
    print(f"Pre visit Hypothesis: {tip[0].just_str()}")


def pop_recursive(state):
    le_stack = stack(state)
    pop(state)
    while len(le_stack) > 1 and le_stack[-2][0].children.index(le_stack[-1][0]) == len(le_stack[-2][0].children) - 1:
        print(f"Recursive pop: {le_stack[-1]}")
        post_visit(le_stack, le_stack[-1])
        pop(state)


# def print_stack(state):
#     le_stack = state[RECURSION_STACK_KEY]
#     for le in le_stack:
#         print(f"({le[1]}) {le[0].just_str()}")


def validate_hypothesis_post_exec(state: CodeExplorerState) -> dict[str, Any]:
    print("In Validation Hypothesis POST-EXEC")
    print("=====================================")

    le_stack = stack(state)

    current = le_stack[-1]

    if isinstance(current[0].node, Hypothesis):
        pre_visit(le_stack, current)
        push(state, (current[0].children[0], 0))
        print(f"After adding children, tip is {le_stack[-1][0].just_str()} with counter {le_stack[-1][1]}...")
        if isinstance(current[0].children[0].node, Evidence):
            print(f"After adding children, parent is {le_stack[-2][0].just_str()} with counter {le_stack[-2][1]}...")
        return generic_return(le_stack, state)

    parent = le_stack[-2]
    # Terminal condition
    print(f"Parent hypo children={parent[0].children}, Parent hypo count={parent[1]}")
    if isinstance(current[0].node, Evidence) and parent[1] == len(parent[0].children):
        print("END OF EVIDENCE\n============================")
        print_stack(state[RECURSION_STACK_KEY])
        pop_recursive(state)
        post_visit(le_stack, le_stack[-1])  # Let it do its post-visit
        processed_with_incomplete_parent = le_stack.pop()  # Pull out remaining child which has also been completed but it still has more siblings to process
        if len(le_stack) == 0:
            return generic_return(le_stack, state)
        current_hypo_index = le_stack[-1][0].children.index(processed_with_incomplete_parent[0])
        print(f"Current hypo index={current_hypo_index}")
        next_index = current_hypo_index + 1
        print(f"Next hypo index={next_index}")
        # next_index = le_stack[-1][1]
        push(state, (le_stack[-1][0].children[next_index], 0))  # Push its sibling onto stack for processing
        print_stack(state[RECURSION_STACK_KEY])
    elif isinstance(current[0].node, Evidence) and parent[1] < len(parent[0].children):
        print("MORE EVIDENCE TO COME\n============================")
        pop(state)
        current_evidence_index = parent[0].children.index(current[0])
        print(f"Pushed next Evidence: {parent[0].children[current_evidence_index + 1]}")
        push(state, (parent[0].children[current_evidence_index + 1], 0))

    return generic_return(le_stack, state)


def generic_return(le_stack, state):
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[],
                             base_hypothesis=state[BASE_HYPOTHESIS_KEY], recursion_stack=le_stack)
