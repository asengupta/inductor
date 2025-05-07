from typing import Any, Dict

from graph.state import MyState
from graph.router_constants import EXIT_DECISION

def reverse_engineering_lead(tool_llm):
    def run_agent(state: MyState) -> Dict[str, Any]:
        print("============IN LEAD===============")
        print(state)
        while True:
            user_input: str = input("What do you want to do? ")
            if user_input.lower() in ["quit", "exit", "q"]:
                return MyState(input=user_input, current_request=user_input,
                               messages=[EXIT_DECISION])
                print("Goodbye!")
                raise Exception("Goodbye!")
            elif user_input.strip() == "":
                print("No input provided. Please try again.")
            else:
                break

        return MyState(input=user_input, current_request=user_input,
                       messages=state["messages"] + [user_input])

    return run_agent
