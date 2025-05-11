from hypothesis import Hypothesis, random_hypothesis
from induction_node import InferenceNode

FREEFORM_EXPLORATION_DECISION = "free_explore_decision"
HYPOTHESIZE_DECISION = "hypothesize_decision"
BUILD_INFERENCE_TREE_DECISION = "build_inference_tree_decision"
VALIDATE_HYPOTHESIS_DECISION = "validate_hypothesis_decision"
SYSTEM_QUERY_DECISION = "system_query_decision"
DONT_KNOW_DECISION = "dont_know_decision"
EXIT_DECISION = "exit_decision"
VISIT_HYPOTHESIS_DECISION = "visit_hypothesis_decision"
VISIT_EVIDENCE_DECISION = "visit_evidence_decision"
DUMMY_INFERENCE_NODE = InferenceNode(random_hypothesis(), [])
CONTINUE_RECURSE_INFERENCE_TREE_DECISION = "continue_recurse_inference_tree_decision"
EXIT_RECURSE_INFERENCE_TREE_DECISION = "exit_recurse_inference_tree_decision"
