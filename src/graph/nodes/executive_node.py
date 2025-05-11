from typing import Any

from graph.router_constants import EXIT_DECISION
from graph.state import CodeExplorerState


def reverse_engineering_lead(tool_llm):
    def run_agent(state: CodeExplorerState) -> dict[str, Any]:
        print("============IN LEAD===============")
        print(state)
        while True:
            user_input: str = input("What do you want to do? ")
            if user_input.lower() in ["quit", "exit", "q"]:
                return CodeExplorerState(input=user_input, current_request=user_input,
                                         messages=[EXIT_DECISION])
                print("Goodbye!")
                raise Exception("Goodbye!")
            elif user_input.strip() == "":
                print("No input provided. Please try again.")
            else:
                break

        return CodeExplorerState(input=user_input, current_request=user_input,
                                 messages=state["messages"] + [user_input])

    return run_agent
