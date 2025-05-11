import json
from typing import Any

from beta_bernoulli_belief import no_evidence, equally_likely
from evidence import Evidence
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, MESSAGES_KEY, INPUT_KEY, INFERENCE_STACK_KEY
from graph.tool_names import CREATE_EVIDENCE_STRATEGY_MCP_TOOL_NAME, BREAKDOWN_HYPOTHESIS_MCP_TOOL_NAME
from hypothesis import Hypothesis
from hypothesis_subject import HypothesisSubject
from hypothesis_object import HypothesisObject
from induction_node import InferenceNode


def as_evidence_inference_node(child) -> InferenceNode:
    return InferenceNode(
        Evidence(child["evidence_description"], contribution_to_hypothesis=child["contribution_to_hypothesis"], belief=no_evidence()))


def as_hypothesis_inference_node(child) -> InferenceNode:
    print(f"Child is of type {type(child)} and is {child}")
    return InferenceNode(
        Hypothesis(HypothesisSubject(child["subject"]["name"]), child["relation"],
                   HypothesisObject(child["object"]["name"]), belief=equally_likely(),
                   contribution_to_root=child["contribution_to_root"]))


def build_inference_node_build(state: CodeExplorerState) -> dict[str, Any]:
    tool_message = state[MESSAGES_KEY][-1]
    tool_name = tool_message.name
    latest_entry = state[INFERENCE_STACK_KEY][-1]
    if tool_name == CREATE_EVIDENCE_STRATEGY_MCP_TOOL_NAME:
        node: InferenceNode = latest_entry[0]
        print(f"TOOL MESSAGE IS: {tool_message.content}")

        all_children = parsed(tool_message.content)
        print(f"Raw Evidences are: {all_children}")
        child_evidences = [as_evidence_inference_node(child) for child in all_children]
        print(f"Number of evidences is: {len(child_evidences)}")
        state[INFERENCE_STACK_KEY][-1] = (node, len(child_evidences) - 1)
        node.add_all(child_evidences)
        # print(f"Inference stack after build: {state['inference_stack']}")
    elif tool_name == BREAKDOWN_HYPOTHESIS_MCP_TOOL_NAME:
        node: InferenceNode = latest_entry[0]
        all_children = parsed(tool_message.content)
        sub_hypotheses = [as_hypothesis_inference_node(child) for child in all_children]
        print(f"Number of sub-hypotheses is: {len(sub_hypotheses)}")
        node.add_all(sub_hypotheses)
        state[INFERENCE_STACK_KEY].append((sub_hypotheses[0], 0))
        # print(f"Inference stack after build: {state['inference_stack']}")
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=state[INFERENCE_STACK_KEY])


def parsed(tool_message_content: str | list[str, dict]):
    tool_message_content = json.loads(tool_message_content)
    return [json.loads(raw_child) for raw_child in tool_message_content] if isinstance(tool_message_content,
                                                                                       list) else [
        tool_message_content]
