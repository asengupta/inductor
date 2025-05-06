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

load_dotenv("./env/.env")


# def build_agent(tool_llm):
#     def run_agent(state: MyState) -> dict[str, Any]:
#         messages = state["messages"]
#         print("Input\n----------\n")
#         print(state)
#         response = tool_llm.invoke(messages)
#         print("LLM Response\n----------\n")
#         print(response.content)
#         print("Messages=============================")
#         return {"messages": [response]}
#
#     return run_agent

def random_picker(tool_llm):
    def run_agent(state: MyState) -> dict[str, Any]:
        messages = state["messages"]
        print("Input\n----------\n")
        print(state)
        response = tool_llm.invoke(messages)
        print("LLM Response\n----------\n")
        print(response.content)
        print("Messages=============================")
        return response.content

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
    return {"step_1_state": "DONE"}


def step_2(state: MyState) -> dict[str, Any]:
    print("In step 2")
    print(state)
    return {"step_2_state": "DONE"}


def step_3(state: MyState) -> dict[str, Any]:
    print("In step 3")
    print(state)
    return {"step_3_state": "DONE"}


def step_4(state: MyState) -> dict[str, Any]:
    print("In step 4")
    print(state)
    return {"step_4_state": "DONE"}


def build_decider(tool_llm):
    def decision(state: MyState) -> str:
        print("In decision")
        # return "step_2"
        messages = state["messages"]
        print("Input\n----------\n")
        print(state)
        response = tool_llm.invoke(messages)
        print("LLM Response\n----------\n")
        print(f"--{response.content}--")
        print("Messages=============================")
        return response.content
        # return "step_3"

    return decision


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


llm = ChatAnthropic(  # type: ignore
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=1024,
)

mcp_client = MultiServerMCPClient(
    {
        # "say_hello": {
        #     "command": "python",
        #     "args": ["/Users/asgupta/code/inductor-langgraph-mcp/src/agent/simple_mcp_server.py"],
        #     "transport": "stdio",
        # },
        # "analyseHLASM": {
        #     "command": "java",
        #     "args": ["-jar", "/Users/asgupta/code/hlasm-analyser/hlasm-mcp-server/target/hlasm-mcp-server-1.0-SNAPSHOT.jar"],
        #     "transport": "stdio",
        # }
    })


@asynccontextmanager
async def make_graph(client: MultiServerMCPClient) -> AsyncGenerator[CompiledStateGraph, Any]:
    async with client:
        mcp_tools = client.get_tools()
        print("SOMETHING")
        # print(mcp_tools)
        llm_with_tool = llm.bind_tools(mcp_tools)

        # agent_runner = build_agent(llm_with_tool)
        agent_decider = build_decider(llm_with_tool)

        workflow = StateGraph(MyState)

        workflow.add_node(step_1)
        workflow.add_node(step_2)
        workflow.add_node(step_3)
        workflow.add_node(step_4)

        # workflow.add_node("agent_runner", agent_runner)
        # workflow.add_node("before_tool", before_tool)
        # workflow.add_node("tool", ToolNode(mcp_tools))
        # workflow.add_node(tool_output)
        # workflow.add_node(before_exit)

        workflow.add_edge(START, "step_1")
        # workflow.add_edge("step_1", "step_2")
        workflow.add_conditional_edges("step_1", agent_decider, {
            "step_2": "step_2",
            "step_3": "step_3",
            "default": "step_1",
        })
        workflow.add_edge("step_2", "step_4")
        workflow.add_edge("step_3", "step_4")
        workflow.add_edge("step_4", END)

        # workflow.add_edge("step_2", "agent_runner")
        # workflow.add_conditional_edges("agent_runner", tools_condition, {
        #     # Translate the condition outputs to nodes in our graph
        #     "tools": "tool",
        #     END: "before_exit"
        # })
        # workflow.add_edge("tool", "tool_output")
        # workflow.add_edge("tool_output", "agent_runner")
        # workflow.add_edge("before_exit", END)

        graph = workflow.compile()
        graph.name = "My Graph"
        yield graph


async def update(user_input: str, graph: CompiledStateGraph):
    print("Sending message: " + user_input)
    result = await graph.ainvoke({"messages":
                                      [
                                          "You are executing a Langgraph task graph, and your job is to assist in the navigation of this graph. Output only the name of the next node without any other text or whitespace.",
                                          HumanMessage(content=user_input)]})
    print("Results")
    for event in result:
        print(event)


async def run_thing():
    async with make_graph(mcp_client) as graph:
        while True:
            try:
                user_input: str = input("What do you want to do? ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                elif user_input.strip() == "":
                    print("No input provided. Please try again.")
                    continue
                await update(user_input, graph)
                continue
            except:
                print("Closing graph")
                break


asyncio.run(run_thing())
print("EXITING...")
