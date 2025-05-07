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

load_dotenv("./env/.env")


def reverse_engineering_lead(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        print("============IN LEAD===============")
        print(state)
        while True:
            user_input: str = input("What do you want to do? ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                raise Exception("Goodbye!")
            elif user_input.strip() == "":
                print("No input provided. Please try again.")
            else:
                break

        prompt = """
                              Based on the input,
                              decide which agent you wish to activate: a hypothesis-gathering agent, an exploration agent,
                              or a hypothesis-validating agent.
                              Output either 'explore', 'hypothesize' or 'validate_hypothesis', 'system_query', or 'dontknow' based on this decision
                              as a single string without any other text or whitespace.
                              The rules are:
                              1) Use the hypothesis gathering agent only for creating hypotheses.
                              2) Use the hypothesis validating agent only for validating hypotheses.
                              3) Use 'explore' when answering general questions about the codebase not related to hypotheses or MCP tools.
                              4) Use 'system_query' when answering questions about the MCP tools themselves.
                              operations, just use the exploration agent.
                              5) If you are not sure what to do, output 'dontknow'.
                              
                              REMEMBER: Do not output any other extraneous text or whitespace.
                              """
        return MyState(input=user_input, current_request=user_input,
                       messages=state["messages"] + [user_input, prompt])

    return run_agent


def collect_data_for_hypothesis(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        print("============IN EXPLORE EVIDENCE===============")
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
                       messages=state["messages"] + [response])

    return run_agent


def reverse_engineering_step_decider(tool_llm):
    def run_agent(state: MyState) -> str:
        messages = state["messages"]
        print("In DECIDING WHICH STEP TO TAKE:\n----------\n")
        print(state)
        # print(state["step_1_state"])
        response = tool_llm.invoke(messages)
        print("LLM Response\n----------\n")
        print(response.content)
        if "explore" in response.content:
            print("Free Explore")
            return "free_explore"
        elif "hypothesize" in response.content:
            print("Hypothesize")
            return "hypothesize"
        elif "validate_hypothesis" in response.content:
            print("Validate Hypothesis")
            return "validate_hypothesis"
        elif "system_query" in response.content:
            print("System Query")
            return "system_query"
        else:
            print("Couldn't determine a path. Directing your question to the Free Exploration Agent.")
            return "free_explore"

    return run_agent


class MyState(TypedDict):
    input: str
    messages: Annotated[list[BaseMessage], add_messages]
    current_request: str
    tool_calls: list[str]


def step_1(state: MyState) -> dict[str, Any]:
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
    human_message = HumanMessage("""
        You have multiple tools to investigate the codebase. Use them to gather upto 5 hypotheses about the codebase.
        Use as many tools at once as needed. At the end of your investigations, list down these hypotheses.
        """)
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
        # return {"messages": [response]}

    return run_agent

def system_query(tool_llm, tools):
    def run_agent(state: MyState) -> dict[str, Any]:
        print("In System Query Mode")
        print("=============================")
        print(state)
        response = tool_llm.invoke([f"The list of Model Context Protocol tools are: {tools}. Answer the following request without using any tools: {state["current_request"]}"])
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
    # return {"step_3_state": "DONE", "messages": message}


def step_4(state: MyState) -> dict[str, Any]:
    print("In step 4")
    print(state)
    return {"step_4_state": "DONE"}


def explore_output(state: MyState) -> dict[str, Any]:
    print("In tool_output...")
    print("=====================")
    print(state)
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"])


def anthropic_model():
    ANTHROPIC_MODEL_ID = os.environ.get("ANTHROPIC_MODEL_ID")
    llm = ChatAnthropic(
        model=ANTHROPIC_MODEL_ID,
        temperature=0,
        max_tokens=1024
    )
    return llm


def bedrock_model():
    AWS_MODEL_ID = os.environ.get("AWS_MODEL_ID")
    AWS_REGION = os.environ.get("AWS_REGION")
    print(f"MODEL_ID={AWS_MODEL_ID}")
    bedrock_model = ChatBedrockConverse(
        model_id=AWS_MODEL_ID,  # or "anthropic.bedrock_model-3-sonnet-20240229-v1:0"
        region_name=AWS_REGION
    )
    return bedrock_model


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

        workflow.add_node("step_1", lead)
        workflow.add_node("dontknow", fallback)
        workflow.add_node("explore_evidence", evidence_gatherer)
        workflow.add_node(hypothesis_exec)
        workflow.add_node("hypothesize", hypothesizer)
        workflow.add_node("free_explore", free_explore(llm_with_tool))
        workflow.add_node("system_query", system_query(llm_with_tool, mcp_tools))
        workflow.add_node(validate_hypothesis)
        # workflow.add_node(step_4)

        # workflow.add_node("agent_runner", agent_runner)
        # workflow.add_node("before_tool", before_tool)
        workflow.add_node("explore_tool", ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node("save_hypotheses_tool", ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node("free_explore_tool", ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node("system_query_tool", ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(explore_output)
        # workflow.add_node(before_exit)

        workflow.add_edge(START, "step_1")
        workflow.add_edge("dontknow", "step_1")

        workflow.add_conditional_edges("step_1", agent_decider, {
            "hypothesize": "hypothesis_exec",
            "validate_hypothesis": "validate_hypothesis",
            "free_explore": "free_explore",
            "system_query": "system_query",
            "dontknow": "dontknow",
            "default": "dontknow",
        })
        workflow.add_edge("hypothesis_exec", "explore_evidence")
        workflow.add_conditional_edges("explore_evidence", tools_condition, {
            "tools": "explore_tool",
            END: "step_1"
        })
        workflow.add_conditional_edges("hypothesize", tools_condition, {
            "tools": "save_hypotheses_tool",
            END: "step_1"
        })
        workflow.add_conditional_edges("free_explore", tools_condition, {
            "tools": "free_explore_tool",
            END: "step_1"
        })

        workflow.add_conditional_edges("system_query", tools_condition, {
            "tools": "system_query_tool",
            END: "step_1"
        })

        # workflow.add_edge("free_explore", "free_explore_tool")
        workflow.add_edge("free_explore_tool", "step_1")
        workflow.add_edge("explore_tool", "explore_output")
        workflow.add_edge("explore_output", "hypothesize")
        workflow.add_edge("save_hypotheses_tool", "step_1")
        workflow.add_edge("system_query_tool", "step_1")

        workflow.add_edge("validate_hypothesis", "step_1")
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
