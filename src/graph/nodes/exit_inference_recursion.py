from langgraph.constants import END

from graph.nodes.state_operations import stack
from graph.router_constants import CONTINUE_RECURSE_INFERENCE_TREE_DECISION, EXIT_RECURSE_INFERENCE_TREE_DECISION
from graph.state import CodeExplorerState


def exit_inference_recursion(state: CodeExplorerState) -> str:
    if len(stack(state)) == 0:
        print("Exiting inference recursion")
        return EXIT_RECURSE_INFERENCE_TREE_DECISION
    print("Continuing inference recursion")
    return CONTINUE_RECURSE_INFERENCE_TREE_DECISION
