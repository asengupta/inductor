import json
from typing import Any

from evidence import Evidence
from graph.state import CodeExplorerState
from hypothesis import Hypothesis, HypothesisSubject, HypothesisObject
from induction_node import InferenceNode


def validate_hypothesis(state: CodeExplorerState) -> dict[str, Any]:
    print("In Validation Hypothesis")
    print("==============================")
    print("Not doing anything yet, just showing the base hypothesis")
    print(state["base_hypothesis"].as_tree())
    return CodeExplorerState(input=state["input"], current_request=state["current_request"],
                             messages=state["messages"], inference_stack=state["inference_stack"],
                             base_hypothesis=state["base_hypothesis"])
