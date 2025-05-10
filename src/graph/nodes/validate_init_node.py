from typing import Any, Dict

from langchain_core.tools import BaseTool

from graph.nodes.types import LLM
from graph.state import MyState


def build_inference_tree_init_node(state: MyState) -> Dict[str, Any]:
    print("Initializing Inference Tree...")
    print("============================================")
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"], inference_stack=[])
