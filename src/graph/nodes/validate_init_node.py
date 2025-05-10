from typing import Any, Dict

from langchain_core.tools import BaseTool

from graph.nodes.types import LLM
from graph.state import MyState
from hypothesis import Hypothesis, HypothesisSubject, HypothesisObject
from induction_node import InferenceNode


def build_inference_tree_init_node(state: MyState) -> Dict[str, Any]:
    print("Initializing Inference Tree...")
    print("============================================")
    base_hypothesis = Hypothesis(HypothesisSubject("codebase"), "is", HypothesisObject("simple"), confidence=0.5,
                                 contribution_to_root=1.0)
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"], inference_stack=[(InferenceNode(base_hypothesis, []), 0)])
