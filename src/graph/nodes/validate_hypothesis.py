from typing import Any

from beta_bernoulli_belief import equally_likely
from evidence import Evidence
from graph.nodes.state_operations import stack, push, pop
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, RECURSION_STACK_KEY
from hypothesis import Hypothesis
from induction_node import InferenceNode


def validate_hypothesis_init(state: CodeExplorerState) -> dict[str, Any]:
    print("In Validation Hypothesis Init")
    print("==============================")
    print("Setting up bookkeeping for the inference stack...")
    # root_hypothesis: InferenceNode = state[BASE_HYPOTHESIS_KEY]
    # root_hypothesis = InferenceNode(Hypothesis.create_from_strings("program", "does not interact with", "user", equally_likely(), 1),
    #                                 [InferenceNode(Hypothesis.create_from_strings("program", "lacks", "input functions", equally_likely(), 0.5),
    #                                                [
    #                                                    InferenceNode(Evidence("Search for common input function patterns", 0.5, equally_likely())),
    #                                                    InferenceNode(Evidence("Analyze function names and docstrings for input-related keywords", 0.5, equally_likely()))
    #                                                ]),
    #                                  InferenceNode(Hypothesis.create_from_strings("program", "lacks", "output functions", equally_likely(), 0.5),
    #                                                [
    #                                                    InferenceNode(Evidence("Search for print statements in the entire codebase using regex pattern matching", 0.5, equally_likely())),
    #                                                    InferenceNode(Evidence("Search for custom output function definitions using regex", 0.5, equally_likely()))
    #                                                ])
    #                                  ])
    root_hypothesis = InferenceNode(Hypothesis.create_from_strings("program", "has", "low complexity", equally_likely(), 1),
                                    [InferenceNode(Evidence("The cyclomatic complexity is low", 0.5, equally_likely()),
                                                   []),
                                     InferenceNode(Evidence("The number of sections is small", 0.5, equally_likely()),
                                                   [])
                                     ])
    print(root_hypothesis.as_tree())

    state["recursion_stack"] = [(root_hypothesis, 0)]
    # recurse(state)
    # print(f"At the end: stack = {stack(state)}")
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY], inference_stack=[],
                             base_hypothesis=root_hypothesis, recursion_stack=state[RECURSION_STACK_KEY])


def gather_evidence_with_tool(state: CodeExplorerState) -> None:
    print(f"Visiting evidence: {stack(state)[-1].just_str()}")


def recurse(state: CodeExplorerState) -> None:
    current = stack(state)[-1]
    if isinstance(current.node, Evidence):
        gather_evidence_with_tool(state)
        return
    visit_hypothesis(state)


def visit_hypothesis(state: CodeExplorerState) -> None:
    current = stack(state)[-1]
    print(f"Visiting hypothesis: {current.just_str()}")
    push(state, current)
    for child in current.children:
        push(state, child)
        recurse(state)
        pop(state)
    pop(state)
