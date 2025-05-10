from graph.nodes.inference_tree_decisions import TREE_COMPLETE, TREE_INCOMPLETE
from graph.state import MyState
from dataclasses_json import dataclass_json

def inference_tree_build_step_decider(state: MyState) -> str:
    stack = state["inference_stack"]
    ssss = stack[0][0]
    print(f"Inference tree build step: {ssss.to_json(indent=2)}")
    most_recent = stack[-1]
    print(
        f"Checking indices: {most_recent[1]} vs. {len(most_recent[0].children)} = {most_recent[1] == len(most_recent[0].children)}")
    # print(f"Checking types: {type(most_recent[1])} {type(len(most_recent[0].children))} = {most_recent[1] == most_recent[0].children}")
    # if most_recent[1] == 0:
    #     state["inference_stack"][-1] = (most_recent[0], most_recent[1] + 1)
    #     state["inference_stack"].append((most_recent[0], 0))
    #     return TREE_INCOMPLETE
    # most_recent = stack[-1]
    # if most_recent[1] == 0:
    #     state["inference_stack"].append((most_recent[0], most_recent[1] + 1))
    #     return TREE_INCOMPLETE
    if len(stack) > 1:
        parent = stack[-2]
        if parent[1] == 0:
            stack[-2] = (parent[0], parent[1] + 1)
            print(f"Pushing child to stack, returning {TREE_INCOMPLETE}")
            return TREE_INCOMPLETE
        elif stack[-1][1] == len(stack[-1][0].children):
            stack[-2] = (parent[0], parent[1] + 1)
            stack.pop()
            ret_code = TREE_COMPLETE if len(stack) == 1 else TREE_INCOMPLETE
            print(f"All children completed, popping up back to parent, returning {ret_code}")
            return ret_code
        else:
            stack[-2] = (parent[0], parent[1] + 1)
            stack.pop()
            stack.append((parent[0].children[parent[1]], 0))
            print(f"All children NOT completed, pushing new peer child, returning {TREE_INCOMPLETE}")
            return TREE_INCOMPLETE
    else:
        print(f"ROOT completed, returning {TREE_COMPLETE}")
        return TREE_COMPLETE
    # if most_recent[1] == len(most_recent[0].children):
    #     print(f"Building {most_recent[0]} is complete...")
    #     if len(stack) == 1:
    #         print("Building full tree is complete...")
    #         return TREE_COMPLETE
    #     state["inference_stack"] = stack[:-1]
    #     return TREE_INCOMPLETE
    # state["inference_stack"] = stack[:-1]
    # parent = state["inference_stack"][-1]
    # updated_index = parent[1] + 1
    # state["inference_stack"][-1] = (parent[0], updated_index)
    # state["inference_stack"].append((parent[0].children[updated_index], 0))
    # return TREE_INCOMPLETE
