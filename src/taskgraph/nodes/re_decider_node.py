from src.taskgraph.nodes.types import LanggraphDeciderNode
from src.taskgraph.router_constants import (
    FREEFORM_EXPLORATION_DECISION, HYPOTHESIZE_DECISION, BUILD_INFERENCE_TREE_DECISION,
    SYSTEM_QUERY_DECISION, DONT_KNOW_DECISION, EXIT_DECISION, VALIDATE_HYPOTHESIS_DECISION
)
from src.taskgraph.state import CodeExplorerState
from src.taskgraph.state_keys import MESSAGES_KEY


def reverse_engineering_step_decider(tool_llm) -> LanggraphDeciderNode:
    def run_agent(state: CodeExplorerState) -> str:
        messages = state[MESSAGES_KEY]
        user_input = messages[-1]
        if user_input.content == EXIT_DECISION:
            return EXIT_DECISION
        elif user_input.content.strip() == "v":
            return VALIDATE_HYPOTHESIS_DECISION

        prompt = f"""         The user request is: "{state['current_request']}".
                              Based on the request, decide which agent you wish to activate. Your choices are:
                              1) Hypothesis-gathering agent
                              2) Inference Tree building agent
                              3) Hypothesis-validating agent
                              4) Exploration agent,
                              5) System Query agent
                              Do not use any tools at this point.
                              Output either '{FREEFORM_EXPLORATION_DECISION}', '{HYPOTHESIZE_DECISION}' or '{BUILD_INFERENCE_TREE_DECISION}', '{SYSTEM_QUERY_DECISION}', or '{DONT_KNOW_DECISION}' based on this decision
                              as a single string without any other text or whitespace.
                              The rules are:
                              1) Use '{HYPOTHESIZE_DECISION}' only for creating hypotheses.
                              2) Use '{BUILD_INFERENCE_TREE_DECISION}' only for building inference trees.
                              3) Use '{VALIDATE_HYPOTHESIS_DECISION}' only for validating hypotheses.
                              4) Use '{FREEFORM_EXPLORATION_DECISION}' when answering general questions about the codebase not related to hypotheses or MCP tools.
                              5) Use '{SYSTEM_QUERY_DECISION}' when answering questions about the MCP tools themselves.
                              operations, just use the exploration agent.
                              5) If you are not sure what to do, output '{DONT_KNOW_DECISION}'.
                              
                              REMEMBER: Do not output any other extraneous text or whitespace.
                              """

        print("In DECIDING WHICH STEP TO TAKE:\n----------\n")
        print(state)
        response = tool_llm.invoke(prompt)
        print("LLM Response\n----------\n")
        print(response.content)
        if FREEFORM_EXPLORATION_DECISION in response.content:
            print("Free Explore")
            return FREEFORM_EXPLORATION_DECISION
        elif BUILD_INFERENCE_TREE_DECISION in response.content:
            print("Build Inference Tree")
            return BUILD_INFERENCE_TREE_DECISION
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
        else:
            print("Couldn't determine a path. Directing your question to the Free Exploration Agent.")
            return FREEFORM_EXPLORATION_DECISION

    return run_agent
