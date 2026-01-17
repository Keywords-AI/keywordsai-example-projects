#!/usr/bin/env python3
"""
Multi-Provider Tracing Example - KeywordsAI Tracing SDK

Tracing across multiple AI providers (OpenAI + Anthropic) in a single workflow.
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

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="multi-provider-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
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

# Try to import and initialize Anthropic (using KeywordsAI proxy if ANTHROPIC_BASE_URL is set)
anthropic_client = None
try:
    from anthropic import Anthropic
    anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL")
    anthropic_client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        base_url=anthropic_base_url if anthropic_base_url else None,
    )
    print("OpenAI and Anthropic SDKs loaded")
except ImportError:
    print("Anthropic SDK not available, will skip Anthropic examples")
    print("OpenAI SDK loaded")


@task(name="openai_step")
def openai_step():
    """Execute an OpenAI completion."""
    print("Calling OpenAI...")
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}]
        )
        content = response.choices[0].message.content or "empty"
        print(f"  OpenAI response received: {content}")
        return content
    except Exception as e:
        print(f"  OpenAI call failed: {e}")
        return "Simulated OpenAI response"


@task(name="anthropic_step")
def anthropic_step():
    """Execute an Anthropic completion."""
    if anthropic_client is None:
        print("Skipping Anthropic (SDK not available)...")
        return "Anthropic SDK not available"
    
    print("Calling Anthropic...")
    try:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        content = response.content[0] if response.content else "empty"
        print(f"  Anthropic response received: {content}")
        return str(content)
    except Exception as e:
        print(f"  Anthropic call failed: {e}")
        return "Simulated Anthropic response"


@workflow(name="multi_llm_workflow")
def run_multi_provider_demo() -> dict:
    """Run a workflow that uses multiple LLM providers."""
    openai_result = openai_step()
    anthropic_result = anthropic_step()
    
    return {
        "openai": openai_result,
        "anthropic": anthropic_result
    }


def main():
    """Run the multi-provider demo."""
    print("Starting Multi-Provider Demo\n")
    
    try:
        result = run_multi_provider_demo()
        print(f"\nResults: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    
    print("\nMulti-provider demo completed.")


if __name__ == "__main__":
    main()
