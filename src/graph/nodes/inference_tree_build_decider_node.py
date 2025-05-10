from graph.nodes.inference_tree_decisions import TREE_COMPLETE, TREE_INCOMPLETE
from graph.state import MyState


def inference_tree_build_step_decider(state: MyState) -> str:
    stack = state["inference_stack"]
    ssss = stack[0][0]
    print("STACK\n================")
    print_stack(stack)
    ssss.as_tree()
    print(f"Top stack counter: {stack[0][1]}")
    # print(f"Inference tree build step: {ssss.to_json(indent=2)}")
    most_recent = stack[-1]
    print(f"Stack top is {most_recent[0].just_str()}")
    input("Press Enter to continue...")
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

    if len(most_recent[0].children) == 0:
        # Just got initialised
        # stack[-2] = (parent[0], parent[1] + 1)
        print(f"Pushed first child to stack already, returning {TREE_INCOMPLETE}")
        return TREE_INCOMPLETE
    if most_recent[1] == len(most_recent[0].children) - 1:
        if len(stack) == 1:
            # Root hypothesis is complete
            print(f"All children completed, TREE COMPLETE")
            return TREE_COMPLETE
        parent = stack[-2]
        # stack[-2] = (parent[0], parent[1] + 1)
        while len(stack) > 0 and stack[-1][1] == len(stack[-1][0].children) - 1:
            pop2 = stack.pop()
            print(f"Popped parent: {pop2[0].just_str()} with count: {pop2[1]}...")
        if len(stack) == 0:
            print(f"All children completed, TREE COMPLETE")
            return TREE_COMPLETE
        incomplete_ancestor = stack[-1]
        print_stack(state["inference_stack"])
        stack[-1] = (incomplete_ancestor[0], incomplete_ancestor[1] + 1)
        print(f"Top stack counter: {stack[0][1]}")
        print(f"Incomplete parent with counter: {stack[-1][1]}")
        print(f"Incomplete parent is: {stack[-1][0].just_str()}")
        stack.append((stack[-1][0].children[stack[-1][1]], 0))
        return TREE_INCOMPLETE
    else:
        print("IN THE ELSE\n======================================")
        # print(f"Before stack.pop() = {len(stack)}")
        # stack.pop()
        # print(f"After stack.pop() = {len(stack)}, {len(state['inference_stack'])}")
        stack[-1] = (most_recent[0], most_recent[1] + 1)
        stack.append((most_recent[0].children[most_recent[1]], 0))
        print(f"All children NOT completed, pushing new peer child, returning {TREE_INCOMPLETE}")
        return TREE_INCOMPLETE

    # if len(stack) > 1:
    #     parent = stack[-2]
    #     if parent[1] == 0:
    #         # stack[-2] = (parent[0], parent[1] + 1)
    #         print(f"Pushed first child to stack already, returning {TREE_INCOMPLETE}")
    #         return TREE_INCOMPLETE
    #     # elif parent[1] == len(parent[0].children):
    #     #     # stack[-2] = (parent[0], parent[1] + 1)
    #     #     print(f"Before stack.pop() = {len(stack)}, {len(state['inference_stack'])}")
    #     #     pop1 = stack.pop()
    #     #     print(f"Popped child: {pop1[0].just_str()}...")
    #     #     # Start popping parents until you reach an incomplete parent
    #     #     while len(stack) > 0 and stack[-1][1] == len(stack[-1][0].children):
    #     #         pop2 = stack.pop()
    #     #         print(f"Popped parent: {pop2[0].just_str()} with count: {pop2[1]}...")
    #     #     print(f"After all stack.pop() = {len(stack)}")
    #     #     if len(stack) == 0:
    #     #         print(f"All children completed, TREE COMPLETE")
    #     #         return TREE_COMPLETE
    #     #     incomplete_ancestor = stack[-1]
    #     #     stack[-1] = (incomplete_ancestor[0], incomplete_ancestor[1] + 1)
    #     #     print(f"Incomplete parent with counter: {stack[-1][1]}")
    #     #     stack.append((stack[-1][0].children[stack[-1][1]], 0))
    #     #     return TREE_INCOMPLETE
    #     #     # ret_code = TREE_COMPLETE if len(stack) == 0 else TREE_INCOMPLETE
    #     #     # return ret_code
    #     else:
    #         # In the middle of iterating through children
    #         print(f"Before stack.pop() = {len(stack)}")
    #         stack.pop()
    #         print(f"After stack.pop() = {len(stack)}, {len(state['inference_stack'])}")
    #         stack[-2] = (parent[0], parent[1] + 1)
    #         stack.append((parent[0].children[parent[1]], 0))
    #         print(f"All children NOT completed, pushing new peer child, returning {TREE_INCOMPLETE}")
    #         return TREE_INCOMPLETE
    # else:
    #     print(f"ROOT completed, returning {TREE_COMPLETE}")
    #     return TREE_COMPLETE
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


def print_stack(stack):
    for st in stack:
        print(f"({st[1]}) {st[0].just_str()}")
