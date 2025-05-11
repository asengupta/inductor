from typing import Any

from beta_bernoulli_belief import equally_likely
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY
from hypothesis import Hypothesis
from hypothesis_subject import HypothesisSubject
from hypothesis_object import HypothesisObject
from induction_node import InferenceNode


def build_inference_tree_init_node(state: CodeExplorerState) -> dict[str, Any]:
    print("Initializing Inference Tree...")
    print("============================================")
    print("Input your hypothesis details and I will attempt to break it down into an inference plan.")
    h_subject = input("Input your hypothesis subject:")
    h_relation = input("Input your hypothesis relation:")
    h_object = input("Input your hypothesis object:")
    # base_hypothesis = Hypothesis(HypothesisSubject("Program"), "uses", HypothesisObject("all registers"),
    #                              belief=Belief(1, 1), contribution_to_root=1.0)
    base_hypothesis = Hypothesis(HypothesisSubject(h_subject), h_relation, HypothesisObject(h_object),
                                 belief=equally_likely(), contribution_to_root=1.0)
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[(InferenceNode(base_hypothesis, []), 0)])
