#!/usr/bin/env python3
"""
Manual Instrumentation Example - KeywordsAI Tracing SDK

Demonstrates explicit module instrumentation for environments where
automatic instrumentation may not work properly.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry with manual instrumentation
keywords_ai = KeywordsAITelemetry(
    app_name="manual-instrumentation-example",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "test-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)

# Initialize OpenAI client (using KeywordsAI proxy if OPENAI_BASE_URL is set)
openai_base_url = os.getenv("OPENAI_BASE_URL")
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "test-key"),
    base_url=openai_base_url if openai_base_url else None,
)

# Try to import Anthropic if available (using KeywordsAI proxy if ANTHROPIC_BASE_URL is set)
anthropic_client = None
try:
    from anthropic import Anthropic
    anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL")
    anthropic_client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        base_url=anthropic_base_url if anthropic_base_url else None,
    )
except ImportError:
    print("Anthropic SDK not available, skipping Anthropic instrumentation")


@task(name="openai_completion")
def openai_completion_task() -> str:
    """Execute an OpenAI completion."""
    try:
        completion = openai_client.chat.completions.create(
            messages=[{"role": "user", "content": "What is the capital of France?"}],
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"  (OpenAI call simulated or failed: {e})")
        return "Simulated OpenAI response"


@task(name="anthropic_completion")
def anthropic_completion_task() -> str:
    """Execute an Anthropic completion."""
    if anthropic_client is None:
        return "Anthropic SDK not available"
    
    try:
        message = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[{"role": "user", "content": "What is the capital of Germany?"}]
        )
        return message.content[0].text if message.content else ""
    except Exception as e:
        print(f"  (Anthropic call simulated or failed: {e})")
        return "Simulated Anthropic response"


@workflow(name="multi_provider_workflow", version=1)
def run_multi_provider_workflow() -> dict:
    """Run a workflow that uses multiple AI providers."""
    print("Running OpenAI completion...")
    openai_result = openai_completion_task()
    print(f"   OpenAI result: {openai_result[:50]}..." if len(openai_result) > 50 else f"   OpenAI result: {openai_result}")
    
    print("Running Anthropic completion...")
    anthropic_result = anthropic_completion_task()
    print(f"   Anthropic result: {anthropic_result[:50]}..." if len(anthropic_result) > 50 else f"   Anthropic result: {anthropic_result}")
    
    return {
        "openai": openai_result,
        "anthropic": anthropic_result
    }


def main():
    """Run the manual instrumentation demo."""
    print("Starting Manual Instrumentation Demo\n")
    
    try:
        result = run_multi_provider_workflow()
        print("\nResults:")
        print(f"   OpenAI: {result['openai'][:100]}..." if len(result['openai']) > 100 else f"   OpenAI: {result['openai']}")
        print(f"   Anthropic: {result['anthropic'][:100]}..." if len(result['anthropic']) > 100 else f"   Anthropic: {result['anthropic']}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    
    print("\nManual instrumentation demo completed.")


if __name__ == "__main__":
    main()
