from typing import Any, Callable, Awaitable

from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent

from evidence import Evidence
from graph.nodes.state_operations import stack
from graph.nodes.types import LLM, EvidenceResult
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY, BASE_HYPOTHESIS_KEY


def visit_evidence_build(llm: LLM, tools: list[BaseTool]) -> Callable[
    [CodeExplorerState], Awaitable[dict[str, Any]]]:
    async def visit_evidence(state: CodeExplorerState) -> dict[str, Any]:
        current = stack(state)[-1]
        print(f"Visiting evidence: {current[0].just_str()}")
        le_stack = stack(state)
        print(f"Evidence is updating count of {le_stack[-2][0].just_str()} from {le_stack[-2][1]} by 1...")
        messages = [
            "You are required to gather evidence for a particular hypothesis using all the tools that are available to you.",
            f"The hypothesis is: {le_stack[-2][0].just_str()}",
            f"The evidence you are required to collect is the following: {current[0].just_str()}",
            f"As output, also list the number of evidences for and against the hypothesis."
        ]

        joined_prompt = "\n".join(messages)
        agent = create_react_agent(model=llm, tools=tools,
                                   response_format=EvidenceResult)

        response = await agent.ainvoke({"messages": [{"role": "user", "content": joined_prompt}]})
        print("Response from gathering evidence")
        # print(f"Response from gathering evidence: {response}")
        print("====================================================================================")
        structured_response = response["structured_response"]
        print(structured_response)
        evidence_node: Evidence = current[0].node
        evidence_node.belief.update((structured_response["for_hypothesis"], structured_response["against_hypothesis"]))
        le_stack[-2] = (le_stack[-2][0], le_stack[-2][1] + 1)
        return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                                 messages=state[MESSAGES_KEY], inference_stack=[],
                                 base_hypothesis=state[BASE_HYPOTHESIS_KEY],
                                 recursion_stack=le_stack, )

    return visit_evidence
