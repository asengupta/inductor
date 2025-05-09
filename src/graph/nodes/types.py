from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

LLM = Runnable[LanguageModelInput, BaseMessage]
