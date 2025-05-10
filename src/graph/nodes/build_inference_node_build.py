import json
from typing import Dict, Any

from evidence import Evidence
from graph.state import MyState
from hypothesis import Hypothesis
from induction_node import InferenceNode


def as_evidence_inference_node(child) -> InferenceNode:
    return InferenceNode(
        Evidence(child["evidence_description"], contribution_to_hypothesis=child["contribution_to_hypothesis"]))


def as_hypothesis_inference_node(child) -> InferenceNode:
    return InferenceNode(
        Hypothesis(child["subject"], child["object"], confidence=0.5,
                   contribution_to_root=child["contribution_to_root"]))


def build_inference_node_build(state: MyState) -> Dict[str, Any]:
    tool_message = state["messages"][-1]
    tool_name = tool_message["name"]
    latest_entry = state["inference_stack"][-1]
    if tool_name == "create_evidence_strategy":
        node: InferenceNode = latest_entry[0]
        all_children = json.loads(tool_message["content"])
        child_evidences = [as_evidence_inference_node(child) for child in all_children]
        state["inference_stack"][-1] = (node, len(child_evidences))
        node.add_all(child_evidences)
    elif tool_name == "breakdown_hypothesis":
        node: InferenceNode = latest_entry[0]
        all_children = json.loads(tool_message["content"])
        sub_hypotheses = [as_hypothesis_inference_node(child) for child in all_children]
        # state["inference_stack"].append((sub_hypotheses[0], 0))
        node.add_all(sub_hypotheses)
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"], inference_stack=[])
