from graph.state import CodeExplorerState
from graph.state_keys import TREE_BUILD_STATUS_KEY


def inference_tree_build_step_decider(state: CodeExplorerState) -> str:
    return state[TREE_BUILD_STATUS_KEY]
