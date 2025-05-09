from graph.state import MyState
from graph.router_constants import (
    FREEFORM_EXPLORATION_DECISION, HYPOTHESIZE_DECISION, VALIDATE_HYPOTHESIS_DECISION,
    SYSTEM_QUERY_DECISION, DONT_KNOW_DECISION, EXIT_DECISION
)

def reverse_engineering_step_decider(tool_llm):
    def run_agent(state: MyState) -> str:
        messages = state["messages"]
        if messages[-1].content == EXIT_DECISION:
            return EXIT_DECISION

        prompt = f"""         The user request is: "{state['current_request']}".
                              Based on the request, decide which agent you wish to activate. Your choices are:
                              1) Hypothesis-gathering agent
                              2) Hypothesis-validating agent
                              3) Exploration agent,
                              4) System Query agent
                              
                              Do not use any tools at this point.
                              Output either '{FREEFORM_EXPLORATION_DECISION}', '{HYPOTHESIZE_DECISION}' or '{VALIDATE_HYPOTHESIS_DECISION}', '{SYSTEM_QUERY_DECISION}', or '{DONT_KNOW_DECISION}' based on this decision
                              as a single string without any other text or whitespace.
                              The rules are:
                              1) Use '{HYPOTHESIZE_DECISION}' only for creating hypotheses.
                              2) Use '{VALIDATE_HYPOTHESIS_DECISION}' only for validating hypotheses.
                              3) Use '{FREEFORM_EXPLORATION_DECISION}' when answering general questions about the codebase not related to hypotheses or MCP tools.
                              4) Use '{SYSTEM_QUERY_DECISION}' when answering questions about the MCP tools themselves.
                              operations, just use the exploration agent.
                              5) If you are not sure what to do, output '{DONT_KNOW_DECISION}'.
                              
                              REMEMBER: Do not output any other extraneous text or whitespace.
                              """

        print("In DECIDING WHICH STEP TO TAKE:\n----------\n")
        print(state)
        # print(state["step_1_state"])
        response = tool_llm.invoke(prompt)
        print("LLM Response\n----------\n")
        print(response.content)
        if FREEFORM_EXPLORATION_DECISION in response.content:
            print("Free Explore")
            return FREEFORM_EXPLORATION_DECISION
        elif VALIDATE_HYPOTHESIS_DECISION in response.content:
            print("Validate Hypothesis")
            return VALIDATE_HYPOTHESIS_DECISION
        elif (HYPOTHESIZE_DECISION in response.content
              or "hypothesis" in response.content.lower()
              or "hypotheses" in response.content.lower()):
            print(HYPOTHESIZE_DECISION)
            return HYPOTHESIZE_DECISION
        elif SYSTEM_QUERY_DECISION in response.content:
            print("System Query")
            return SYSTEM_QUERY_DECISION
        elif SYSTEM_QUERY_DECISION in response.content:
            print("System Query")
            return SYSTEM_QUERY_DECISION
        else:
            print("Couldn't determine a path. Directing your question to the Free Exploration Agent.")
            return FREEFORM_EXPLORATION_DECISION

    return run_agent
