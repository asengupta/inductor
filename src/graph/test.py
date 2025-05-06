import boto3
import json

from dotenv import load_dotenv


class ClaudeBedrock:
    def __init__(self, model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0"):
        """
        Initialize the Claude Bedrock client.

        Args:
            model_id: The ID of the Claude model to use.
                     Available models include:
                     - anthropic.claude-3-opus-20240229-v1:0
                     - anthropic.claude-3-sonnet-20240229-v1:0
                     - anthropic.claude-3-haiku-20240307-v1:0
                     - anthropic.claude-2:1
                     - anthropic.claude-instant-v1
        """
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='eu-central-1'  # Change to your region
        )
        self.model_id = model_id

    def generate_text(self, prompt, max_tokens=1000, temperature=0.7):
        """
        Generate text using Claude on AWS Bedrock.

        Args:
            prompt: The text prompt to send to Claude
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 1.0)

        Returns:
            The generated text response
        """
        # Prepare the request payload for Claude models
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # Invoke the model
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )

        # Parse and return the response
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']

    def chat(self, messages, max_tokens=1000, temperature=0.7):
        """
        Have a chat-based conversation with Claude.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 1.0)

        Returns:
            The generated text response
        """
        # Prepare the request payload for Claude models
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        # Invoke the model
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )

        # Parse and return the response
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']

# Example usage
if __name__ == "__main__":
    load_dotenv("./env/.env")

    # Create a Claude client
    claude = ClaudeBedrock()

    # Example 1: Simple text generation
    response = claude.generate_text("Explain quantum computing in simple terms.")
    print("Response:", response)

    # Example 2: Chat-based conversation
    messages = [
        {"role": "user", "content": "Hello, can you tell me about AWS Bedrock?"},
        {"role": "assistant", "content": "AWS Bedrock is Amazon's fully managed service that offers a choice of high-performing foundation models from leading AI companies."},
        {"role": "user", "content": "What models are available besides Claude?"}
    ]
    chat_response = claude.chat(messages)
    print("\nChat Response:", chat_response)
