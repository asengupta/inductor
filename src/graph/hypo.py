import asyncio
import os
from contextlib import asynccontextmanager
from typing import TypedDict, Any, AsyncGenerator, Annotated

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_aws.chat_models.bedrock import ChatBedrockConverse
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from graph.node_names import COLLECT_DATA_FOR_HYPOTHESIS, HYPOTHESIZE, EXPLORE_FREELY, SYSTEM_QUERY, \
    DATA_FOR_HYPOTHESIS_TOOL, SAVE_HYPOTHESES_TOOL, EXPLORE_FREELY_TOOL, SYSTEM_QUERY_TOOL, \
    COLLECT_DATA_FOR_HYPOTHESIS_TOOL_OUTPUT, HYPOTHESIS_GATHER_START, VALIDATE_HYPOTHESIS, DONT_KNOW, EXECUTIVE_AGENT
from graph.router_constants import DONT_KNOW_DECISION, SYSTEM_QUERY_DECISION, FREEFORM_EXPLORATION_DECISION, \
    VALIDATE_HYPOTHESIS_DECISION, HYPOTHESIZE_DECISION, EXIT_DECISION

load_dotenv("./env/.env")

AWS_MODEL_ID = "AWS_MODEL_ID"
AWS_REGION = "AWS_REGION"
ANTHROPIC_MODEL_ID = "ANTHROPIC_MODEL_ID"


def reverse_engineering_lead(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
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


def collect_data_for_hypothesis(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        print("============IN COLLECT DATA TO BUILD HYPOTHESIS===============")
        msg = """
        You have multiple tools to investigate the codebase. Use as many of them as needed to get some initial
        info about the codebase. This info will be ultimately used to hypothesize about the large-scale purpose
        of the codebase and the small-scale purpose of its various sections.
        """
        messages = state["messages"]
        print(f"Asking explorer to: {msg}")
        response = tool_llm.invoke(msg)
        print(response.content)
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"] + [response], llm_response=response)

    return run_agent


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
        elif (HYPOTHESIZE_DECISION in response.content
              or "hypothesis" in response.content.lower()
              or "hypotheses" in response.content.lower()):
            print(HYPOTHESIZE_DECISION)
            return HYPOTHESIZE_DECISION
        elif VALIDATE_HYPOTHESIS_DECISION in response.content:
            print("Validate Hypothesis")
            return VALIDATE_HYPOTHESIS_DECISION
        elif SYSTEM_QUERY_DECISION in response.content:
            print("System Query")
            return SYSTEM_QUERY_DECISION
        else:
            print("Couldn't determine a path. Directing your question to the Free Exploration Agent.")
            return FREEFORM_EXPLORATION_DECISION

    return run_agent


class MyState(TypedDict):
    input: str
    messages: Annotated[list[BaseMessage], add_messages]
    current_request: str
    tool_calls: list[str]
    llm_response: list[BaseMessage]


def executive_init(state: MyState) -> dict[str, Any]:
    print("In step 1")
    print(state)
    user_input: str = input("What do you want to do? ")
    print(state)

    return MyState(input=user_input, current_request=user_input, messages=state["messages"])


def fallback(state: MyState) -> dict[str, Any]:
    print("THIS IS A FALLBACK NODE, GOING BACK TO ROOT==============")
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"])


def hypothesis_exec(state: MyState):
    print("============IN HYPO EXEC=================")
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"] + [])


def hypothesize(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
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


def free_explore(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        print("In Free Exploration Mode")
        print("=============================")
        print(state)
        response = tool_llm.invoke(["""
        You have multiple tools at your disposal to investigate this codebase. Use as many tools at once as needed. 
        """, state["current_request"]])
        print(response.content)
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"] + [response])

    return run_agent


def system_query(tool_llm, tools):
    def run_agent(state: MyState) -> dict[str, Any]:
        print("In System Query Mode")
        print("=============================")
        print(state)
        response = tool_llm.invoke([
            f"The list of Model Context Protocol tools are: {tools}. Answer the following request without using any tools: {state["current_request"]}"])
        print(response.content)
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"] + [response])

    return run_agent


def validate_hypothesis(state: MyState) -> dict[str, Any]:
    print("In validating hypothesis")
    print("=====================")
    print(state)
    message = "Validation of hypothesis not yet implemented"
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"] + [message])


def step_4(state: MyState) -> dict[str, Any]:
    print("In step 4")
    print(state)
    return {"step_4_state": "DONE"}


def generic_tool_output(tool_name: str):
    def show_output(state: MyState) -> dict[str, Any]:
        print(f"In tool_output of {tool_name}...")
        print("=====================")
        print(state)
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"])

    return show_output


def anthropic_model():
    anthropic_model_id = os.environ.get(ANTHROPIC_MODEL_ID)
    llm = ChatAnthropic(
        model=anthropic_model_id,
        temperature=0,
        max_tokens=1024
    )
    return llm


def bedrock_model():
    aws_model_id = os.environ.get(AWS_MODEL_ID)
    aws_region = os.environ.get(AWS_REGION)
    print(f"MODEL_ID={aws_model_id}")
    bedrock = ChatBedrockConverse(
        model_id=aws_model_id,  # or "anthropic.bedrock_model-3-sonnet-20240229-v1:0"
        region_name=aws_region
    )
    return bedrock


mcp_client = MultiServerMCPClient(
    {
        "say_hello": {
            "command": "python",
            "args": ["/Users/asgupta/code/inductor-langgraph-mcp/src/agent/simple_mcp_server.py"],
            "transport": "stdio",
        },
        "analyseHLASM": {
            "command": "java",
            "args": ["-jar",
                     "/Users/asgupta/code/hlasm-analyser/hlasm-mcp-server/target/hlasm-mcp-server-1.0-SNAPSHOT.jar"],
            "transport": "stdio",
        },
        "hypothesis": {
            "command": "python",
            "args": ["/Users/asgupta/code/inductor-langgraph-mcp/src/agent/hypothesis_mcp_server.py"],
            "transport": "stdio",
        }
    })


@asynccontextmanager
async def make_graph(client: MultiServerMCPClient) -> AsyncGenerator[CompiledStateGraph, Any]:
    async with client:
        mcp_tools = client.get_tools()
        print("SOMETHING")
        # print(mcp_tools)
        llm_with_tool = anthropic_model().bind_tools(mcp_tools, tool_choice="auto")
        # llm_with_tool = bedrock_model().bind_tools(mcp_tools)
        agent_decider = reverse_engineering_step_decider(llm_with_tool)
        lead = reverse_engineering_lead(llm_with_tool)
        evidence_gatherer = collect_data_for_hypothesis(llm_with_tool)
        hypothesizer = hypothesize(llm_with_tool)

        workflow = StateGraph(MyState)

        workflow.add_node(EXECUTIVE_AGENT, lead)
        workflow.add_node(DONT_KNOW, fallback)
        workflow.add_node(COLLECT_DATA_FOR_HYPOTHESIS, evidence_gatherer)
        workflow.add_node(HYPOTHESIS_GATHER_START, hypothesis_exec)
        workflow.add_node(HYPOTHESIZE, hypothesizer)
        workflow.add_node(EXPLORE_FREELY, free_explore(llm_with_tool))
        workflow.add_node(SYSTEM_QUERY, system_query(llm_with_tool, mcp_tools))
        workflow.add_node(VALIDATE_HYPOTHESIS, validate_hypothesis)
        # workflow.add_node(step_4)

        # workflow.add_node("agent_runner", agent_runner)
        # workflow.add_node("before_tool", before_tool)
        workflow.add_node(DATA_FOR_HYPOTHESIS_TOOL, ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(SAVE_HYPOTHESES_TOOL, ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(EXPLORE_FREELY_TOOL, ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(SYSTEM_QUERY_TOOL, ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(COLLECT_DATA_FOR_HYPOTHESIS_TOOL_OUTPUT, generic_tool_output(DATA_FOR_HYPOTHESIS_TOOL))
        # workflow.add_node(before_exit)

        workflow.add_edge(START, EXECUTIVE_AGENT)
        workflow.add_edge(DONT_KNOW, EXECUTIVE_AGENT)

        workflow.add_conditional_edges(EXECUTIVE_AGENT, agent_decider, {
            HYPOTHESIZE_DECISION: HYPOTHESIS_GATHER_START,
            VALIDATE_HYPOTHESIS_DECISION: VALIDATE_HYPOTHESIS,
            FREEFORM_EXPLORATION_DECISION: EXPLORE_FREELY,
            SYSTEM_QUERY_DECISION: SYSTEM_QUERY,
            DONT_KNOW_DECISION: DONT_KNOW,
            EXIT_DECISION: END,
            "default": DONT_KNOW,
        })
        workflow.add_edge(HYPOTHESIS_GATHER_START, COLLECT_DATA_FOR_HYPOTHESIS)
        workflow.add_conditional_edges(COLLECT_DATA_FOR_HYPOTHESIS, tools_condition, {
            "tools": DATA_FOR_HYPOTHESIS_TOOL,
            END: EXECUTIVE_AGENT
        })
        workflow.add_conditional_edges(HYPOTHESIZE, tools_condition, {
            "tools": SAVE_HYPOTHESES_TOOL,
            END: EXECUTIVE_AGENT
        })
        workflow.add_conditional_edges(EXPLORE_FREELY, tools_condition, {
            "tools": EXPLORE_FREELY_TOOL,
            END: EXECUTIVE_AGENT
        })

        workflow.add_conditional_edges(SYSTEM_QUERY, tools_condition, {
            "tools": SYSTEM_QUERY_TOOL,
            END: EXECUTIVE_AGENT
        })

        # workflow.add_edge("free_explore", "FREE_EXPLORE_TOOL")
        workflow.add_edge(EXPLORE_FREELY, EXECUTIVE_AGENT)
        workflow.add_edge(DATA_FOR_HYPOTHESIS_TOOL, COLLECT_DATA_FOR_HYPOTHESIS_TOOL_OUTPUT)
        workflow.add_edge(COLLECT_DATA_FOR_HYPOTHESIS_TOOL_OUTPUT, HYPOTHESIZE)
        workflow.add_edge(SAVE_HYPOTHESES_TOOL, EXECUTIVE_AGENT)
        workflow.add_edge(SYSTEM_QUERY_TOOL, EXECUTIVE_AGENT)

        workflow.add_edge(VALIDATE_HYPOTHESIS, EXECUTIVE_AGENT)
        # workflow.add_edge("step_4", END)

        graph = workflow.compile()
        graph.name = "My Graph"
        yield graph


async def update(user_input: str, graph: CompiledStateGraph):
    result = await graph.ainvoke({"messages":
        [
            """
            You are part of a reverse engineering pipeline looking at a HLASM codebase. Help navigate the user in understanding this code.
            """,
            HumanMessage(content=user_input)]})
    print("Results")
    for event in result:
        print(event)


async def run_thing():
    async with make_graph(mcp_client) as graph:
        # user_input: str = input("What do you want to do? ")
        await update("", graph)
        # while True:
        #     try:
        #         user_input: str = input("What do you want to do? ")
        #         if user_input.lower() in ["quit", "exit", "q"]:
        #             print("Goodbye!")
        #             break
        #         elif user_input.strip() == "":
        #             print("No input provided. Please try again.")
        #             continue
        #         await update(user_input, graph)
        #         continue
        #     except:
        #         print("Closing graph")
        #         break


asyncio.run(run_thing())
print("EXITING...")
