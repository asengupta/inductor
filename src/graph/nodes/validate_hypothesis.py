import json
from typing import Any

from evidence import Evidence
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, INFERENCE_STACK_KEY
from graph.tool_names import BASE_HYPOTHESIS_KEY
from hypothesis import Hypothesis, HypothesisSubject, HypothesisObject
from induction_node import InferenceNode


def validate_hypothesis(state: CodeExplorerState) -> dict[str, Any]:
    print("In Validation Hypothesis")
    print("==============================")
    print("Not doing anything yet, just showing the base hypothesis")
    print(state[BASE_HYPOTHESIS_KEY].as_tree())
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=state[INFERENCE_STACK_KEY],
                             base_hypothesis=state[BASE_HYPOTHESIS_KEY])
