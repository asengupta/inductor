from typing import Any

from langchain_core.messages import HumanMessage

from graph.nodes.types import LLM, LanggraphNode
from graph.state import CodeExplorerState
from graph.state_keys import CURRENT_REQUEST_KEY, INPUT_KEY, MESSAGES_KEY


def hypothesize(tool_llm: LLM) -> LanggraphNode:
    def run_agent(state: CodeExplorerState) -> dict[str, Any]:
        print("IN HYPOTHESIZER....================================================================")
        messages = state[MESSAGES_KEY]
        human_message = HumanMessage("""
            The previous steps have gathered some evidence of the codebase to gather hypotheses.
            Use the evidence to gather upto 5 hypotheses about the codebase. Do not start gathering any
            other evidence at this point, only use the information already available.
            List down these hypotheses.
            Each hypothesis should enumerate the subject, the object, and the relation between them, as
            well as the confidence in this hypothesized relation. Each hypothesis should be specific and
            testable using the available tools.
            After that, create/persist these multiple hypotheses at once using the appropriate tool.
            """)
        response = tool_llm.invoke(messages + [human_message])
        print(response.content)
        # return {"messages": [response]}
        return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                                 messages=state[MESSAGES_KEY] + [response])

    return run_agent

def hypothesis_exec(state: CodeExplorerState):
    print("============IN HYPO EXEC=================")
    return CodeExplorerState(input=state[INPUT_KEY], current_request=state[CURRENT_REQUEST_KEY],
                             messages=state[MESSAGES_KEY] + [])
