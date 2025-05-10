from typing import Any, Dict

from langchain_core.tools import BaseTool

from graph.nodes.types import LLM
from graph.state import MyState
from hypothesis import Hypothesis, HypothesisSubject, HypothesisObject
from induction_node import InferenceNode


def build_inference_tree_init_node(state: MyState) -> Dict[str, Any]:
    print("Initializing Inference Tree...")
    print("============================================")
    print("Input your hypothesis details and I will attempt to break it down into an inference plan.")
    h_subject = input("Input your hypothesis subject:")
    h_relation = input("Input your hypothesis relation:")
    h_object = input("Input your hypothesis object:")
    # base_hypothesis = Hypothesis(HypothesisSubject("Program"), "uses", HypothesisObject("all registers"), confidence=0.5,
    #                              contribution_to_root=1.0)
    base_hypothesis = Hypothesis(HypothesisSubject(h_subject), h_relation, HypothesisObject(h_object), confidence=0.5,
                                 contribution_to_root=1.0)
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"], inference_stack=[(InferenceNode(base_hypothesis, []), 0)])
