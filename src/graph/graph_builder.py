import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from graph.models import anthropic_model
from graph.node_names import (
    COLLECT_DATA_FOR_HYPOTHESIS, HYPOTHESIZE, EXPLORE_FREELY, SYSTEM_QUERY,
    DATA_FOR_HYPOTHESIS_TOOL, SAVE_HYPOTHESES_TOOL, EXPLORE_FREELY_TOOL, SYSTEM_QUERY_TOOL,
    COLLECT_DATA_FOR_HYPOTHESIS_TOOL_OUTPUT, HYPOTHESIS_GATHER_START, DECOMPOSE_HYPOTHESIS, DONT_KNOW,
    EXECUTIVE_AGENT, BREAKDOWN_HYPOTHESIS_TOOL, BUILD_INFERENCE_TREE_INIT,
    BUILD_INFERENCE_NODE_BUILD, INFERENCE_TREE_BUILD_STEP_CALCULATOR, VISIT_HYPOTHESIS, VISIT_EVIDENCE,
    VALIDATE_HYPOTHESIS_INIT, VALIDATE_HYPOTHESIS_EXEC
)
from graph.nodes.build_inference_node_build import build_inference_node_build
from graph.nodes.build_inference_tree_init import build_inference_tree_init_node
from graph.nodes.collect_data_node import collect_data_for_hypothesis
from graph.nodes.decompose_hypothesis import decompose_hypothesis
from graph.nodes.executive_node import reverse_engineering_lead
from graph.nodes.explore_node import free_explore
from graph.nodes.hypothesize_node import hypothesize, hypothesis_exec
from graph.nodes.inference_tree_build_decider_node import inference_tree_build_step_decider
from graph.nodes.inference_tree_build_next_step_calculator import inference_tree_build_step_calculator
from graph.nodes.inference_tree_decisions import TREE_INCOMPLETE, TREE_COMPLETE
from graph.nodes.re_decider_node import reverse_engineering_step_decider
from graph.nodes.system_query_node import system_query
from graph.nodes.tool_output_node import generic_tool_output
from graph.nodes.travel_inference_tree_decider import goto_hypothesis_or_evidence_or_exit
from graph.nodes.utility_nodes import fallback
from graph.nodes.validate_hypothesis import validate_hypothesis_init
from graph.nodes.validate_hypothesis_pre_exec import validate_hypothesis_pre_exec
from graph.nodes.visit_evidence import visit_evidence
from graph.nodes.visit_hypothesis import visit_hypothesis
from graph.router_constants import (
    DONT_KNOW_DECISION, SYSTEM_QUERY_DECISION, FREEFORM_EXPLORATION_DECISION,
    BUILD_INFERENCE_TREE_DECISION, HYPOTHESIZE_DECISION, EXIT_DECISION, VALIDATE_HYPOTHESIS_DECISION, VISIT_HYPOTHESIS_DECISION, VISIT_EVIDENCE_DECISION
)
from graph.state import CodeExplorerState
from graph.state_keys import MESSAGES_KEY
from graph.tool_names import CREATE_EVIDENCE_STRATEGY_MCP_TOOL_NAME, BREAKDOWN_HYPOTHESIS_MCP_TOOL_NAME

load_dotenv("./env/.env")

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


def as_json(state: CodeExplorerState) -> str:
    if not state[MESSAGES_KEY]:
        return str(state)
    tool_result = state[MESSAGES_KEY][-1]
    return json.loads(tool_result.content)


@asynccontextmanager
async def make_graph(client: MultiServerMCPClient) -> AsyncGenerator[CompiledStateGraph, Any]:
    async with client:
        mcp_tools: list[BaseTool] = client.get_tools()
        inference_tree_building_tools = [tool for tool in mcp_tools if
                                         tool.name in [CREATE_EVIDENCE_STRATEGY_MCP_TOOL_NAME,
                                                       BREAKDOWN_HYPOTHESIS_MCP_TOOL_NAME]]
        # print(mcp_tools)
        llm_with_tool = anthropic_model().bind_tools(mcp_tools, tool_choice="auto")
        # llm_with_tool = bedrock_model().bind_tools(mcp_tools)
        agent_decider = reverse_engineering_step_decider(llm_with_tool)
        lead = reverse_engineering_lead(llm_with_tool)
        evidence_gatherer = collect_data_for_hypothesis(llm_with_tool)
        hypothesizer = hypothesize(llm_with_tool)

        workflow = StateGraph(CodeExplorerState)

        workflow.add_node(EXECUTIVE_AGENT, lead)
        workflow.add_node(DONT_KNOW, fallback)
        workflow.add_node(COLLECT_DATA_FOR_HYPOTHESIS, evidence_gatherer)
        workflow.add_node(HYPOTHESIS_GATHER_START, hypothesis_exec)
        workflow.add_node(HYPOTHESIZE, hypothesizer)
        workflow.add_node(EXPLORE_FREELY, free_explore(llm_with_tool))
        workflow.add_node(SYSTEM_QUERY, system_query(llm_with_tool, mcp_tools))
        workflow.add_node(BUILD_INFERENCE_TREE_INIT, build_inference_tree_init_node)
        workflow.add_node(DECOMPOSE_HYPOTHESIS, decompose_hypothesis(llm_with_tool, inference_tree_building_tools))
        workflow.add_node(BUILD_INFERENCE_NODE_BUILD, build_inference_node_build)
        workflow.add_node(INFERENCE_TREE_BUILD_STEP_CALCULATOR, inference_tree_build_step_calculator)
        workflow.add_node(VALIDATE_HYPOTHESIS_INIT, validate_hypothesis_init)
        workflow.add_node(VALIDATE_HYPOTHESIS_EXEC, validate_hypothesis_pre_exec)
        workflow.add_node(VISIT_HYPOTHESIS, visit_hypothesis)
        workflow.add_node(VISIT_EVIDENCE, visit_evidence)

        workflow.add_node(DATA_FOR_HYPOTHESIS_TOOL, ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(SAVE_HYPOTHESES_TOOL, ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(EXPLORE_FREELY_TOOL, ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(SYSTEM_QUERY_TOOL, ToolNode(mcp_tools, handle_tool_errors=True))
        workflow.add_node(COLLECT_DATA_FOR_HYPOTHESIS_TOOL_OUTPUT, generic_tool_output(DATA_FOR_HYPOTHESIS_TOOL))
        workflow.add_node(BREAKDOWN_HYPOTHESIS_TOOL, ToolNode(mcp_tools, handle_tool_errors=True))
        # workflow.add_node(before_exit)

        workflow.add_edge(START, EXECUTIVE_AGENT)
        workflow.add_edge(DONT_KNOW, EXECUTIVE_AGENT)

        workflow.add_conditional_edges(EXECUTIVE_AGENT, agent_decider, {
            HYPOTHESIZE_DECISION: HYPOTHESIS_GATHER_START,
            BUILD_INFERENCE_TREE_DECISION: BUILD_INFERENCE_TREE_INIT,
            VALIDATE_HYPOTHESIS_DECISION: VALIDATE_HYPOTHESIS_INIT,
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

        workflow.add_edge(BUILD_INFERENCE_TREE_INIT, DECOMPOSE_HYPOTHESIS)
        workflow.add_conditional_edges(DECOMPOSE_HYPOTHESIS, tools_condition, {
            "tools": BREAKDOWN_HYPOTHESIS_TOOL,
            END: EXECUTIVE_AGENT
        })

        # workflow.add_edge("free_explore", "FREE_EXPLORE_TOOL")
        workflow.add_edge(EXPLORE_FREELY, EXPLORE_FREELY_TOOL)
        workflow.add_edge(EXPLORE_FREELY_TOOL, EXECUTIVE_AGENT)
        workflow.add_edge(DATA_FOR_HYPOTHESIS_TOOL, COLLECT_DATA_FOR_HYPOTHESIS_TOOL_OUTPUT)
        workflow.add_edge(COLLECT_DATA_FOR_HYPOTHESIS_TOOL_OUTPUT, HYPOTHESIZE)
        workflow.add_edge(SAVE_HYPOTHESES_TOOL, EXECUTIVE_AGENT)
        workflow.add_edge(SYSTEM_QUERY_TOOL, EXECUTIVE_AGENT)
        workflow.add_edge(BREAKDOWN_HYPOTHESIS_TOOL, BUILD_INFERENCE_NODE_BUILD)
        workflow.add_edge(BUILD_INFERENCE_NODE_BUILD, INFERENCE_TREE_BUILD_STEP_CALCULATOR)
        workflow.add_edge(VALIDATE_HYPOTHESIS_INIT, VALIDATE_HYPOTHESIS_EXEC)
        workflow.add_edge(VISIT_HYPOTHESIS, VALIDATE_HYPOTHESIS_EXEC)
        workflow.add_edge(VISIT_EVIDENCE, VALIDATE_HYPOTHESIS_EXEC)
        workflow.add_conditional_edges(VALIDATE_HYPOTHESIS_EXEC, goto_hypothesis_or_evidence_or_exit, {
            VISIT_HYPOTHESIS_DECISION: VISIT_HYPOTHESIS,
            VISIT_EVIDENCE_DECISION: VISIT_EVIDENCE,
            END: EXECUTIVE_AGENT
        })
        workflow.add_conditional_edges(INFERENCE_TREE_BUILD_STEP_CALCULATOR, inference_tree_build_step_decider, {
            TREE_INCOMPLETE: DECOMPOSE_HYPOTHESIS,
            TREE_COMPLETE: EXECUTIVE_AGENT,
            "default": EXECUTIVE_AGENT
        })

        graph = workflow.compile()
        graph.name = "My Graph"
        yield graph


async def start_task_graph(user_input: str, graph: CompiledStateGraph) -> None:
    await graph.ainvoke({"messages":
        [
            """
            You are part of a reverse engineering pipeline looking at a HLASM codebase. Help navigate the user in understanding this code.
            """,
            HumanMessage(content=user_input)]}, {"recursion_limit": 500})
    print("Goodbye!")


async def run_thing() -> None:
    async with make_graph(mcp_client) as graph:
        await start_task_graph("", graph)


if __name__ == "__main__":
    asyncio.run(run_thing())
    print("EXITING...")
