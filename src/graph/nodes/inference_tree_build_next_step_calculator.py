from typing import Any

from graph.nodes.inference_tree_decisions import TREE_COMPLETE, TREE_INCOMPLETE
from graph.state import CodeExplorerState
from induction_node import InferenceNode


def stateful(state, tree_build_status: str, root_node: InferenceNode) -> dict[str, Any]:
    return CodeExplorerState(input=state["input"], current_request=state["current_request"],
                             messages=state["messages"], inference_stack=state["inference_stack"],
                             tree_build_status=tree_build_status, base_hypothesis=root_node)


def inference_tree_build_step_calculator(state: CodeExplorerState) -> dict[str, Any]:
    stack = state["inference_stack"]
    ssss = stack[0][0]
    print("STACK\n================")
    print_stack(stack)
    ssss.as_tree()
    print(f"Top stack counter: {stack[0][1]}")
    # print(f"Inference tree build step: {ssss.to_json(indent=2)}")
    most_recent = stack[-1]
    print(f"Stack top is {most_recent[0].just_str()}")
    # input("Press Enter to continue...")
    print(
        f"Checking indices: {most_recent[1]} vs. {len(most_recent[0].children)} = {most_recent[1] == len(most_recent[0].children)}")
    if len(most_recent[0].children) == 0:
        # Just got initialised
        print(f"Pushed first child to stack already, returning {TREE_INCOMPLETE}")
        return stateful(state, TREE_INCOMPLETE, stack[0][0])
        # return TREE_INCOMPLETE
    if most_recent[1] == len(most_recent[0].children) - 1:
        # Terminal behaviour when children are all Evidence objects
        while len(stack) > 0 and stack[-1][1] == len(stack[-1][0].children) - 1:
            pop2 = stack.pop()
            print(f"Popped parent: {pop2[0].just_str()} with count: {pop2[1]}...")
        if len(stack) == 0:
            # state["base_hypothesis"] = pop2[0]
            print(f"All children completed, TREE COMPLETE")
            return stateful(state, TREE_COMPLETE, pop2[0])
        incomplete_ancestor = stack[-1]
        print_stack(state["inference_stack"])
        # Go to next child of current incomplete ancestor
        stack[-1] = (incomplete_ancestor[0], incomplete_ancestor[1] + 1)
        print(f"Top stack counter: {stack[0][1]}")
        print(f"Incomplete parent with counter: {stack[-1][1]}")
        print(f"Incomplete parent is: {stack[-1][0].just_str()}")
        stack.append((stack[-1][0].children[stack[-1][1]], 0))
        return stateful(state, TREE_INCOMPLETE, stack[0][0])
    else:
        raise (Exception("Cannot come here"))


def print_stack(stack):
    for st in stack:
        print(f"({st[1]}) {st[0].just_str()}")
