from functools import reduce
from typing import Any

from beta_bernoulli_belief import BetaBernoulliBelief, no_evidence
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, BASE_HYPOTHESIS_KEY, RECURSION_STACK_KEY
from induction_node import InferenceNode


def aggregate_distributions(total_belief: BetaBernoulliBelief, belief: BetaBernoulliBelief) -> BetaBernoulliBelief:
    return BetaBernoulliBelief(total_belief.alpha + belief.alpha, total_belief.beta + belief.beta)


def update_posteriors_recursively(node: InferenceNode):
    if len(node.children) == 0:
        return node.node.belief
    total_belief_for_node = reduce(lambda agg, prb: aggregate_distributions(agg, update_posteriors_recursively(prb)), node.children,
           no_evidence())
    node.node.belief = total_belief_for_node
    return total_belief_for_node


def update_posteriors(state: CodeExplorerState) -> dict[str, Any]:
    print("Updating posteriors\n========================================")
    base_hypothesis: InferenceNode = state[BASE_HYPOTHESIS_KEY]
    print(f"Before: {base_hypothesis.as_tree()}")
    print(f"Belief in hypothesis before was: {base_hypothesis.node.belief.mean()}")
    update_posteriors_recursively(base_hypothesis)
    print(f"After: {base_hypothesis.as_tree()}")
    print(f"Belief in hypothesis after is: {base_hypothesis.node.belief.mean()}")
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[],
                             base_hypothesis=base_hypothesis,
                             recursion_stack=state[RECURSION_STACK_KEY])
