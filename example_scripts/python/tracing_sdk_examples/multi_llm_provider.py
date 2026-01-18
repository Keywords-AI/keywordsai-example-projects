usage_)#!/usr/bin/env python3
"""
Multi-LLM Provider Tracing Example - KeywordsAI Tracing SDK

Demonstrates tracing across multiple AI providers (OpenAI + Anthropic) in a single workflow.
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry - block HTTP noise but allow LLM provider instrumentation
keywords_ai = KeywordsAITelemetry(
    app_name="multi-llm-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

# OpenAI client
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "test-key"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
)

# Anthropic client (optional)
anthropic_client = None
try:
    from anthropic import Anthropic
    anthropic_client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        base_url=os.getenv("ANTHROPIC_BASE_URL") or None,
    )
    print("Loaded: OpenAI + Anthropic")
except ImportError:
    print("Loaded: OpenAI only (Anthropic SDK not installed)")


@task(name="task_openai")
async def task_openai(prompt: str) -> str:
    """Call OpenAI GPT-3.5."""
    print("   [OpenAI] Calling gpt-3.5-turbo...")
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
        )
        result = response.choices[0].message.content or ""
        print(f"   [OpenAI] Response: {result[:50]}...")
        return result
    except Exception as e:
        print(f"   [OpenAI] Error: {e}")
        return f"OpenAI Error: {e}"


@task(name="task_anthropic")
async def task_anthropic(prompt: str) -> str:
    """Call Anthropic Claude."""
    if anthropic_client is None:
        print("   [Anthropic] Skipped (SDK not installed)")
        return "Anthropic SDK not available"
    
    print("   [Anthropic] Calling claude-3-haiku...")
    try:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        result = response.content[0].text if response.content else ""
        print(f"   [Anthropic] Response: {result[:50]}...")
        return result
    except Exception as e:
        print(f"   [Anthropic] Error: {e}")
        return f"Anthropic Error: {e}"


@task(name="task_combine")
async def task_combine(openai_result: str, anthropic_result: str) -> str:
    """Combine results from both providers."""
    print("   [Combine] Merging responses...")
    combined = f"OpenAI said: {openai_result[:30]}... | Anthropic said: {anthropic_result[:30]}..."
    print(f"   [Combine] Done")
    return combined


@workflow(name="multi_llm_workflow")
async def multi_llm_workflow(user_prompt: str) -> dict:
    """Workflow that queries multiple LLM providers and combines results."""
    client = get_client()
    
    if client:
        client.update_current_span(
            keywordsai_params={
                "customer_identifier": "multi_llm_user",
                "thread_identifier": f"thread_{os.getpid()}",
                "metadata": {"prompt": user_prompt},
            },
        )
    
    # Query both providers
    openai_result = await task_openai(user_prompt)
    anthropic_result = await task_anthropic(user_prompt)
    
    # Combine results
    combined = await task_combine(openai_result, anthropic_result)
    
    return {
        "openai": openai_result,
        "anthropic": anthropic_result,
        "combined": combined,
    }


async def main():
    print("=" * 60)
    print("Multi-LLM Provider Demo")
    print("=" * 60)
    print("\nExpected hierarchy:")
    print("  multi_llm_workflow (root)")
    print("  +-- task_openai")
    print("  +-- task_anthropic")
    print("  +-- task_combine\n")
    
    try:
        result = await multi_llm_workflow("Say hello in one sentence.")
        print(f"\n--- Results ---")
        print(f"OpenAI: {result['openai']}")
        print(f"Anthropic: {result['anthropic']}")
        print(f"Combined: {result['combined']}")
    finally:
        print("\nFlushing...")
        keywords_ai.flush()
        await asyncio.sleep(2)
    
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
