from typing import Any, Dict

from langchain_core.tools import BaseTool

from graph.nodes.types import LLM
from graph.state import MyState


def build_inference_node(tool_llm: LLM, tools: list[BaseTool]) -> Dict[str, Any]:
    def run_agent(state: MyState) -> Dict[str, Any]:
        print("In validating hypothesis")
        print("=====================")
        messages = state["messages"]
        current_hypothesis = state["inference_stack"][-1]
        message = "Validation of hypothesis not yet implemented"
        prompt = f"The hypothesis is: {current_hypothesis}."
        generic_breakdown_prompt = f"""
        Based on the list of tools provided, you have only two options:
        1) If you think you can gather evidence for this hypothesis directly,
        call the 'create_evidence_strategy' tool with the list of evidences needed to be gathered,
        along with the name of the tools you will use to gather these evidences. For each
        evidence, also provide its percentage of contribution to proving the root hypothesis.
        2) If you think this hypothesis needs to be broken down further into smaller, more testable hypotheses,
        call the 'breakdown_hypothesis' tool with the list of the sub-hypotheses you come up with. For each
        sub-hypothesis, also provide its percentage of contribution to proving the root hypothesis.
        The list of tools are: {tools}
        """
        print(f"The prompt is:\n{prompt}")
        response = tool_llm.invoke([prompt, generic_breakdown_prompt])
        print(response.content)
        # return {"messages": [response]}
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=[response], inference_stack=state["inference_stack"])

    return run_agent
