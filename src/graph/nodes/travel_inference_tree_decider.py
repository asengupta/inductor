from langgraph.constants import END

from evidence import Evidence
from graph.nodes.state_operations import stack
from graph.router_constants import VISIT_EVIDENCE_DECISION, VISIT_HYPOTHESIS_DECISION
from graph.state import CodeExplorerState
from hypothesis import Hypothesis


def goto_hypothesis_or_evidence_or_exit(state: CodeExplorerState) -> str:
    recursion_stack = stack(state)
    if len(recursion_stack) == 0:
        return END
    current = recursion_stack[-1][0].node
    print(f"CURRENT TYPE: {type(current)}")
    if isinstance(current, Evidence):
        return VISIT_EVIDENCE_DECISION
    elif isinstance(current, Hypothesis):
        return VISIT_HYPOTHESIS_DECISION
    return END
