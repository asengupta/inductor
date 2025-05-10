import json
from typing import Dict, Any

from evidence import Evidence
from graph.nodes.inference_tree_decisions import TREE_COMPLETE, TREE_INCOMPLETE
from graph.state import MyState
from graph.router_constants import (
    FREEFORM_EXPLORATION_DECISION, HYPOTHESIZE_DECISION, VALIDATE_HYPOTHESIS_DECISION,
    SYSTEM_QUERY_DECISION, DONT_KNOW_DECISION, EXIT_DECISION
)
from hypothesis import Hypothesis
from induction_node import InferenceNode


def as_evidence_inference_node(child) -> InferenceNode:
    return InferenceNode(
        Evidence(child["evidence_description"], contribution_to_hypothesis=child["contribution_to_hypothesis"]))


def as_hypothesis_inference_node(child) -> InferenceNode:
    return InferenceNode(
        Hypothesis(child["subject"], child["object"], confidence=0.5, contribution_to_root=child["contribution_to_root"]))


def build_inference_node_build(state: MyState) -> Dict[str, Any]:
    tool_message = state["messages"][-1]
    tool_name = tool_message["name"]
    if tool_name == "create_evidence_strategy":
        node = state["inference_stack"]
        all_children = json.loads(tool_message["content"])
        child_evidences = [as_evidence_inference_node(child) for child in all_children]
        node.add_all(child_evidences)
    elif tool_name == "breakdown_hypothesis":
        node = state["inference_stack"]
        all_children = json.loads(tool_message["content"])
        sub_hypotheses = [as_hypothesis_inference_node(child) for child in all_children]
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"], inference_stack=[])
