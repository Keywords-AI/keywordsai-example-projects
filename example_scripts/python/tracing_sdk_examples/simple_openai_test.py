#!/usr/bin/env python3
"""
Simple OpenAI Test - KeywordsAI Tracing SDK

Simple test demonstrating OpenAI integration with global instance pattern.
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow
from keywordsai_tracing.instruments import Instruments

# Global KeywordsAI instance (similar to TypeScript pattern)
_keywords_ai: Optional[KeywordsAITelemetry] = None

# Initialize OpenAI client (using KeywordsAI proxy if OPENAI_BASE_URL is set)
openai_base_url = os.getenv("OPENAI_BASE_URL")
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "test-api-key"),
    base_url=openai_base_url if openai_base_url else None,
)


@dataclass
class ChatMessage:
    """A chat message."""
    role: str  # 'user', 'assistant', 'system'
    content: str


@dataclass
class ChatCompletionResult:
    """Result from a chat completion."""
    message: str
    usage: Optional[dict]
    model: str
    id: str


@workflow(name="generateChatCompletion")
def generate_chat_completion(
    messages: list[ChatMessage],
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7
) -> ChatCompletionResult:
    """Generate a chat completion using OpenAI."""
    global _keywords_ai
    
    if _keywords_ai is None:
        raise RuntimeError(
            "KeywordsAI not initialized. Make sure instrumentation is set up correctly."
        )
    
    try:
        completion = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature,
        )
        
        return ChatCompletionResult(
            message=completion.choices[0].message.content or "",
            usage=dict(completion.usage) if completion.usage else None,
            model=completion.model,
            id=completion.id,
        )
    except Exception as e:
        print(f"OpenAI API error: {e}")
        raise


def simple_openai_test():
    """Run a simple OpenAI test with KeywordsAI tracing."""
    global _keywords_ai
    
    print("Simple OpenAI + KeywordsAI Test\n")
    
    # Initialize KeywordsAI (block instruments without installed OpenTelemetry packages)
    _keywords_ai = KeywordsAITelemetry(
        app_name="simple-openai-test",
        api_key=os.getenv("KEYWORDSAI_API_KEY", "test-api-key"),
        base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
        block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
    )
    
    print("KeywordsAI setup complete\n")
    
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="What is Python?"),
    ]
    
    try:
        print("Sending request to OpenAI...")
        result = generate_chat_completion(messages)
        
        print("Success!")
        print(f"Response: {result.message}")
        print(f"Usage: {result.usage}")
        print(f"ID: {result.id}")
        
    except Exception as e:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "test-api-key" or api_key.startswith("your_"):
            print("No valid OPENAI_API_KEY found, skipping real API call")
            print("In a real scenario, the instrumentation would capture the request and response automatically.")
        else:
            print(f"Error: {e}")
    
    print("\nTest completed!")


if __name__ == "__main__":
    simple_openai_test()
