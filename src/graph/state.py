from numbers import Number
from typing import TypedDict, Any, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from induction_node import InferenceNode


class MyState(TypedDict):
    input: str
    messages: Annotated[list[BaseMessage], add_messages]
    current_request: str
    tool_calls: list[str]
    llm_response: list[BaseMessage]
    inference_stack: list[tuple[InferenceNode, Number]]
