from typing import TypedDict, Any, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class MyState(TypedDict):
    input: str
    messages: Annotated[list[BaseMessage], add_messages]
    current_request: str
    tool_calls: list[str]
    llm_response: list[BaseMessage]
