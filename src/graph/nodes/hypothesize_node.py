from typing import Any, Dict
from langchain_core.messages import HumanMessage

from graph.state import MyState

def hypothesize(tool_llm):
    def run_agent(state: MyState) -> Dict[str, Any]:
        print("IN HYPOTHESIZER....================================================================")
        messages = state["messages"]
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
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"] + [response])

    return run_agent

def hypothesis_exec(state: MyState):
    print("============IN HYPO EXEC=================")
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"] + [])
