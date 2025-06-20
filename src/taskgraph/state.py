from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from src.domain.induction_node import InferenceNode


class CodeExplorerState(TypedDict):
    input: str
    messages: Annotated[list[BaseMessage], add_messages]
    current_request: str
    tool_calls: list[str]
    llm_response: list[BaseMessage]
    inference_stack: list[tuple[InferenceNode, int]]
    base_hypothesis: InferenceNode
    tree_build_status: str
    recursion_stack: list[tuple[InferenceNode, int]]
