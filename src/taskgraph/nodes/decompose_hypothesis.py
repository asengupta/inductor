from typing import Any

from langchain_core.tools import BaseTool

from src.taskgraph.nodes.types import LLM, LanggraphNode
from src.taskgraph.state import CodeExplorerState
from src.taskgraph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, INFERENCE_STACK_KEY
from src.taskgraph.tool_names import CREATE_EVIDENCE_STRATEGY_MCP_TOOL_NAME, BREAKDOWN_HYPOTHESIS_MCP_TOOL_NAME


def decompose_hypothesis(tool_llm: LLM, tools: list[BaseTool]) -> LanggraphNode:
    def run_agent(state: CodeExplorerState) -> dict[str, Any]:
        print("In Decomposing Hypothesis")
        print("============================")
        messages = state[MESSAGES_KEY]
        print(f"Stack length is {len(state[INFERENCE_STACK_KEY])}")
        current_hypothesis = state[INFERENCE_STACK_KEY][-1][0].node
        message = "Validation of hypothesis not yet implemented"
        prompt = f"The hypothesis is: {current_hypothesis}."
        generic_breakdown_prompt = f"""
        Based on the list of tools provided, you have the following options:
        1) If you think you can gather evidence for this hypothesis directly using the tools provided,
        call the '{CREATE_EVIDENCE_STRATEGY_MCP_TOOL_NAME}' tool with the list of evidences needed to be gathered,
        along with the name of the tools you will use to gather these evidences. For each
        evidence, also provide its percentage of contribution to proving the root hypothesis. Since you
        have not gathered any evidence, belief in this evidence will be zero.
        2) If you think this hypothesis needs to be broken down further into smaller, more testable hypotheses,
        call the '{BREAKDOWN_HYPOTHESIS_MCP_TOOL_NAME}' tool with the list of the sub-hypotheses you come up with.
        A testable hypothesis is one which is specific to the codebase and unambiguous, and can
        be verified with the tools provided.
        For each sub-hypothesis, also provide its percentage of contribution to proving the root hypothesis.
        3) If the stack depth is more than 2, you must use the '{CREATE_EVIDENCE_STRATEGY_MCP_TOOL_NAME}' tool.
        
        
        The current stack depth is {len(state[INFERENCE_STACK_KEY])}.
        Limit the sub-hypotheses and evidences to 2 or less.
        The list of tools are: {tools}
        """
        print(f"The prompt is:\n{prompt}")
        response = tool_llm.invoke([prompt, generic_breakdown_prompt])
        # print(response.content)
        # return {"messages": [response]}
        return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                                 messages=[response], inference_stack=state[INFERENCE_STACK_KEY])

    return run_agent
