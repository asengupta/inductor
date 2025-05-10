from typing import Any, Dict

from langchain_core.tools import BaseTool

from graph.nodes.types import LLM
from graph.state import MyState


def decompose_hypothesis(tool_llm: LLM, tools: list[BaseTool]) -> Dict[str, Any]:
    def run_agent(state: MyState) -> Dict[str, Any]:
        print("In validating hypothesis")
        print("=====================")
        messages = state["messages"]
        print(f"Stack length is {len(state["inference_stack"])}")
        current_hypothesis = state["inference_stack"][-1][0].node
        message = "Validation of hypothesis not yet implemented"
        prompt = f"The hypothesis is: {current_hypothesis}."
        generic_breakdown_prompt = f"""
        Based on the list of tools provided, you have the following options:
        1) If you think you can gather evidence for this hypothesis directly,
        call the 'create_evidence_strategy' tool with the list of evidences needed to be gathered,
        along with the name of the tools you will use to gather these evidences. For each
        evidence, also provide its percentage of contribution to proving the root hypothesis.
        2) If you think this hypothesis needs to be broken down further into smaller, more testable hypotheses,
        call the 'breakdown_hypothesis' tool with the list of the sub-hypotheses you come up with. For each
        sub-hypothesis, also provide its percentage of contribution to proving the root hypothesis.
        3) If the stack depth is more than 3, you must use the 'create_evidence_strategy' tool.
        
        
        The current stack depth is {len(state["inference_stack"])}.
        Limit the sub-hypotheses and evidences to 2.
        The list of tools are: {tools}
        """
        print(f"The prompt is:\n{prompt}")
        response = tool_llm.invoke([prompt, generic_breakdown_prompt])
        # print(response.content)
        # return {"messages": [response]}
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=[response], inference_stack=state["inference_stack"])

    return run_agent
