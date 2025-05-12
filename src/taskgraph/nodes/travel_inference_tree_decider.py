from langgraph.constants import END

from src.domain.evidence import Evidence
from src.taskgraph.nodes.state_operations import stack, print_stack
from src.taskgraph.router_constants import VISIT_EVIDENCE_DECISION, VISIT_HYPOTHESIS_DECISION
from src.taskgraph.state import CodeExplorerState
from src.domain.hypothesis import Hypothesis


def goto_hypothesis_or_evidence(state: CodeExplorerState) -> str:
    recursion_stack = stack(state)
    # print("In DECIDER\n=======================")
    # print_stack(recursion_stack)
    # if len(recursion_stack) == 0:
    #     return END
    current = recursion_stack[-1][0].node
    print(f"CURRENT TYPE: {type(current)}")
    if isinstance(current, Evidence):
        return VISIT_EVIDENCE_DECISION
    elif isinstance(current, Hypothesis):
        return VISIT_HYPOTHESIS_DECISION
    return END
