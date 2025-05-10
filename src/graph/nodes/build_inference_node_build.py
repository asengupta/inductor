import json
from typing import Dict, Any

from evidence import Evidence
from graph.state import MyState
from hypothesis import Hypothesis, HypothesisSubject, HypothesisObject
from induction_node import InferenceNode


def as_evidence_inference_node(child) -> InferenceNode:
    return InferenceNode(
        Evidence(child["evidence_description"], contribution_to_hypothesis=child["contribution_to_hypothesis"]))


def as_hypothesis_inference_node(child) -> InferenceNode:
    print(f"Child is of type {type(child)} and is {child}")
    return InferenceNode(
        Hypothesis(HypothesisSubject(child["subject"]["name"]), child["relation"],
                   HypothesisObject(child["object"]["name"]), confidence=0.5,
                   contribution_to_root=child["contribution_to_root"]))


def build_inference_node_build(state: MyState) -> Dict[str, Any]:
    tool_message = state["messages"][-1]
    tool_name = tool_message.name
    latest_entry = state["inference_stack"][-1]
    if tool_name == "create_evidence_strategy":
        node: InferenceNode = latest_entry[0]
        print(f"TOOL MESSAGE IS: {tool_message.content}")

        all_children = parsed(tool_message.content)
        print(f"Raw Evidences are: {all_children}")
        child_evidences = [as_evidence_inference_node(child) for child in all_children]
        print(f"Number of evidences is: {len(child_evidences)}")
        state["inference_stack"][-1] = (node, len(child_evidences) - 1)
        node.add_all(child_evidences)
        # print(f"Inference stack after build: {state['inference_stack']}")
    elif tool_name == "breakdown_hypothesis":
        node: InferenceNode = latest_entry[0]
        all_children = parsed(tool_message.content)
        sub_hypotheses = [as_hypothesis_inference_node(child) for child in all_children]
        print(f"Number of sub-hypotheses is: {len(sub_hypotheses)}")
        node.add_all(sub_hypotheses)
        state["inference_stack"].append((sub_hypotheses[0], 0))
        # print(f"Inference stack after build: {state['inference_stack']}")
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"], inference_stack=state["inference_stack"])


def parsed(tool_message_content: str | list[str, dict]):
    tool_message_content = json.loads(tool_message_content)
    return [json.loads(raw_child) for raw_child in tool_message_content] if isinstance(tool_message_content,
                                                                                       list) else [
        tool_message_content]
