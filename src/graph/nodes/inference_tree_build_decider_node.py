from graph.nodes.inference_tree_decisions import TREE_COMPLETE, TREE_INCOMPLETE
from graph.state import MyState


def inference_tree_build_step_decider(state: MyState) -> str:
    stack = state["inference_stack"]
    most_recent = stack[-1]
    if most_recent[1] == most_recent[0].children:
        print(f"Building {most_recent[0]} is complete...")
        if len(stack) == 1:
            print("Building full tree is complete...")
            return TREE_COMPLETE
        state["inference_stack"] = stack[:-1]
        return TREE_INCOMPLETE
    s = stack[:-1]
    s.append((most_recent[0].children[most_recent[1]], 0))
    stack[-1] = (most_recent[0], most_recent[1] + 1)
    return TREE_COMPLETE
