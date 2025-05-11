from graph.state import CodeExplorerState
from graph.state_keys import TREE_BUILD_STATUS_KEY


def inference_tree_build_step_decider(state: CodeExplorerState) -> str:
    return state[TREE_BUILD_STATUS_KEY]


def print_stack(stack):
    for st in stack:
        print(f"({st[1]}) {st[0].just_str()}")
