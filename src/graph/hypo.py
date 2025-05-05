import asyncio
from contextlib import asynccontextmanager
from typing import TypedDict, Any, AsyncGenerator, Annotated

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
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
        print(state)
        user_input: str = input("What do you want to do? ")
        return {"messages": [user_input, """
                              Based on the input,
                              decide which agent you wish to activate: a hypothesis-gathering agent or a hypothesis-validating agent.
                              Output either 'hypothesize' or 'validate_hypothesis' based on this decision
                              as a single string without any other text or whitespace.
                              """
                             ]}

    return run_agent


def explore_evidence(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        messages = state["messages"]
        response = tool_llm.invoke(messages)
        print(response)
        return {"messages": [response]}

    return run_agent


def reverse_engineering_step_decider(tool_llm):
    def run_agent(state: MyState) -> str:
        messages = state["messages"]
        print("Input\n----------\n")
        print(state)
        response = tool_llm.invoke(messages)
        print("LLM Response\n----------\n")
        print(response.content)
        print("Messages=============================")
        return "hypothesize"
        # return response.content

    return run_agent


class MyState(TypedDict):
    input: str
    step_1_state: str
    step_2_state: str
    step_3_state: str
    step_4_state: str
    exiting_state: str
    messages: Annotated[list[BaseMessage], add_messages]
    tool_calls: list[str]


def step_1(state: MyState) -> dict[str, Any]:
    print("In step 1")
    print(state)
    user_input: str = input("What do you want to do? ")
    print(state)
    return {"step_1_state": "DONE", "messages": user_input}


def hypothesis_exec(state: MyState):
    human_message = HumanMessage("""
        You have multiple tools to investigate the codebase. Use them to gather upto 5 hypotheses about the codebase.
        Use as many tools at once as needed. At the end of your investigations, list down these hypotheses.
        """)
    return {"messages": [human_message]}


def hypothesize(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        messages = state["messages"]
        human_message = HumanMessage("""
            The previous steps have gathered some evidence of the codebase to gather hypotheses.
            Use the evidence to gather upto 5 hypotheses about the codebase. List down these hypotheses.
            """)
        response = tool_llm.invoke(messages + [human_message])
        print(response.content)
        return {"messages": [response]}

    return run_agent


def validate_hypothesis(state: MyState) -> dict[str, Any]:
    print("In validating hypothesis")
    print(state)
    return {"step_3_state": "DONE"}


def step_4(state: MyState) -> dict[str, Any]:
    print("In step 4")
    print(state)
    return {"step_4_state": "DONE"}


# def before_tool(state: MyState) -> dict[str, Any]:
#     print("In before tool")
#     print(state)
#     return {}
#
#
# def tool_output(state: MyState) -> dict[str, Any]:
#     print("In tool_output...")
#     print(state)
#     return {"tool_output_state": "DONE"}
#
#
# def before_exit(state: MyState) -> dict[str, Any]:
#     print("Before exit...")
#     print(state)
#     return {"exiting_state": "DONE"}


llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=1024,
)

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
        }
    })


@asynccontextmanager
async def make_graph(client: MultiServerMCPClient) -> AsyncGenerator[CompiledStateGraph, Any]:
    async with client:
        mcp_tools = client.get_tools()
        print("SOMETHING")
        # print(mcp_tools)
        llm_with_tool = llm.bind_tools(mcp_tools)

        agent_decider = reverse_engineering_step_decider(llm_with_tool)
        lead = reverse_engineering_lead(llm_with_tool)
        evidence_gatherer = explore_evidence(llm_with_tool)
        hypothesizer = hypothesize(llm_with_tool)

        workflow = StateGraph(MyState)

        workflow.add_node("step_1", lead)
        workflow.add_node("explore_evidence", evidence_gatherer)
        workflow.add_node(hypothesis_exec)
        workflow.add_node("hypothesize", hypothesizer)
        workflow.add_node(validate_hypothesis)
        # workflow.add_node(step_4)

        # workflow.add_node("agent_runner", agent_runner)
        # workflow.add_node("before_tool", before_tool)
        workflow.add_node("tool", ToolNode(mcp_tools))
        # workflow.add_node(tool_output)
        # workflow.add_node(before_exit)

        workflow.add_edge(START, "step_1")
        workflow.add_conditional_edges("step_1", agent_decider, {
            "hypothesize": "hypothesis_exec",
            "validate_hypothesis": "validate_hypothesis",
            "default": "step_1",
        })
        workflow.add_edge("hypothesis_exec", "explore_evidence")
        workflow.add_conditional_edges("explore_evidence", tools_condition, {
            # Translate the condition outputs to nodes in our graph
            "tools": "tool",
            END: "step_1"
        })
        workflow.add_edge("tool", "hypothesize")
        workflow.add_edge("hypothesize", "step_1")

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
