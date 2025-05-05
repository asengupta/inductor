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
                              Output either 'explore', 'hypothesize' or 'validate_hypothesis' based on this decision
                              as a single string without any other text or whitespace.
                              """
        return MyState(input=user_input, current_request=user_input,
                       messages=state["messages"] + [user_input, prompt])

    return run_agent


def explore_evidence(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        messages = state["messages"]
        response = tool_llm.invoke(messages)
        print(response)
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"] + [response])

    return run_agent


def reverse_engineering_step_decider(tool_llm):
    def run_agent(state: MyState) -> str:
        messages = state["messages"]
        print("Input\n----------\n")
        print(state)
        # print(state["step_1_state"])
        response = tool_llm.invoke(messages)
        print("LLM Response\n----------\n")
        print(response.content)
        if "explore" in response.content:
            print("Explore")
            return "explore"
        elif "hypothesize" in response.content:
            print("Hypothesize")
            return "hypothesize"
        elif "validate_hypothesis" in response.content:
            print("Validate Hypothesis")
            return "validate_hypothesis"
        else:
            print("Couldn't determine a path. Please phrase your question more clearly.")
            return "step_1"

    return run_agent


class MyState(TypedDict):
    input: str
    step_1_state: str
    step_2_state: str
    step_3_state: str
    step_4_state: str
    exiting_state: str
    messages: Annotated[list[BaseMessage], add_messages]
    current_request: str
    tool_calls: list[str]


def step_1(state: MyState) -> dict[str, Any]:
    print("In step 1")
    print(state)
    user_input: str = input("What do you want to do? ")
    print(state)

    return MyState(input=user_input, current_request=user_input, messages=state["messages"])


def hypothesis_exec(state: MyState):
    human_message = HumanMessage("""
        You have multiple tools to investigate the codebase. Use them to gather upto 5 hypotheses about the codebase.
        Use as many tools at once as needed. At the end of your investigations, list down these hypotheses.
        """)
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"] + [human_message])


def hypothesize(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        messages = state["messages"]
        human_message = HumanMessage("""
            The previous steps have gathered some evidence of the codebase to gather hypotheses.
            Use the evidence to gather upto 5 hypotheses about the codebase. List down these hypotheses.
            Each hypothesis should enumerate the subject, the object, and the relation between them, as
            well as the confidence in this hypothesized relation.
            After that, persist these hypotheses individually using the appropriate tool.
            """)
        response = tool_llm.invoke(messages + [human_message])
        print(response.content)
        # return {"messages": [response]}
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"] + [response])

    return run_agent


def explore(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        print("In explore")
        print("=====================")
        print(state)
        response = tool_llm.invoke(state["current_request"])
        print(response.content)
        return MyState(input=state["input"], current_request=state["current_request"],
                       messages=state["messages"] + [response])
        # return {"messages": [response]}

    return run_agent


def validate_hypothesis(state: MyState) -> dict[str, Any]:
    print("In validating hypothesis")
    print(state)
    message = "Validation of hypothesis not yet implemented"
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"] + [message])
    # return {"step_3_state": "DONE", "messages": message}


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
def explore_output(state: MyState) -> dict[str, Any]:
    print("In tool_output...")
    print(state)
    return MyState(input=state["input"], current_request=state["current_request"],
                   messages=state["messages"])


#
#
# def before_exit(state: MyState) -> dict[str, Any]:
#     print("Before exit...")
#     print(state)
#     return {"exiting_state": "DONE"}


llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=1024
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
        llm_with_tool = llm.bind_tools(mcp_tools, tool_choice="auto")

        agent_decider = reverse_engineering_step_decider(llm_with_tool)
        lead = reverse_engineering_lead(llm_with_tool)
        evidence_gatherer = explore_evidence(llm_with_tool)
        hypothesizer = hypothesize(llm_with_tool)

        workflow = StateGraph(MyState)

        workflow.add_node("step_1", lead)
        workflow.add_node("explore_evidence", evidence_gatherer)
        workflow.add_node(hypothesis_exec)
        workflow.add_node("hypothesize", hypothesizer)
        workflow.add_node("explore", explore(llm_with_tool))
        workflow.add_node(validate_hypothesis)
        # workflow.add_node(step_4)

        # workflow.add_node("agent_runner", agent_runner)
        # workflow.add_node("before_tool", before_tool)
        workflow.add_node("explore_tool", ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node("save_hypotheses_tool", ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(explore_output)
        # workflow.add_node(before_exit)

        workflow.add_edge(START, "step_1")
        workflow.add_conditional_edges("step_1", agent_decider, {
            "hypothesize": "hypothesis_exec",
            "validate_hypothesis": "validate_hypothesis",
            "explore": "explore",
            "default": "step_1",
        })
        workflow.add_edge("hypothesis_exec", "explore_evidence")
        workflow.add_conditional_edges("explore_evidence", tools_condition, {
            # Translate the condition outputs to nodes in our graph
            "tools": "explore_tool",
            END: "step_1"
        })
        workflow.add_conditional_edges("hypothesize", tools_condition, {
            # Translate the condition outputs to nodes in our graph
            "tools": "save_hypotheses_tool",
            END: "step_1"
        })
        workflow.add_edge("explore_tool", "explore_output")
        workflow.add_edge("explore_output", "hypothesize")
        workflow.add_edge("save_hypotheses_tool", "step_1")

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
