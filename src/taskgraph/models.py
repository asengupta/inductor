import os

from langchain_anthropic import ChatAnthropic
from langchain_aws.chat_models.bedrock import ChatBedrockConverse
from langchain_ollama import OllamaLLM, ChatOllama

AWS_MODEL_ID = "AWS_MODEL_ID"
AWS_REGION = "AWS_REGION"
ANTHROPIC_MODEL_ID = "ANTHROPIC_MODEL_ID"


def anthropic_model():
    anthropic_model_id = os.environ.get(ANTHROPIC_MODEL_ID)
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0,
        max_tokens=1024
    )
    return llm


def ollama_model():
    return ChatOllama(model="mistral")


def bedrock_model():
    aws_model_id = os.environ.get(AWS_MODEL_ID)
    aws_region = os.environ.get(AWS_REGION)
    print(f"MODEL_ID={aws_model_id}")
    bedrock = ChatBedrockConverse(
        model_id=aws_model_id,  # or "anthropic.bedrock_model-3-sonnet-20240229-v1:0"
        region_name=aws_region
    )
    return bedrock
