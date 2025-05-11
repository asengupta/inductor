from langgraph.constants import END

from graph.nodes.state_operations import stack
from graph.router_constants import CONTINUE_RECURSE_INFERENCE_TREE_DECISION
from graph.state import CodeExplorerState
from graph.state_keys import TREE_BUILD_STATUS_KEY


def exit_inference_recursion(state: CodeExplorerState) -> str:
    if len(stack(state)) == 1:
        return END
    return CONTINUE_RECURSE_INFERENCE_TREE_DECISION
