from typing import Any, Callable, TypedDict

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

from graph.state import CodeExplorerState

LLM = Runnable[LanguageModelInput, BaseMessage]
LanggraphNode = Callable[[CodeExplorerState], dict[str, Any]]
LanggraphDeciderNode = Callable[[CodeExplorerState], str]

class EvidenceResult(TypedDict):
    for_hypothesis: int
    against_hypothesis: int
