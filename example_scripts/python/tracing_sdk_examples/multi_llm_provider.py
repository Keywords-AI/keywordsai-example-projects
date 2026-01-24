#!/usr/bin/env python3
"""
Multi-LLM Provider - KeywordsAI Tracing SDK
Demonstrates: tracing across OpenAI + Anthropic in one workflow
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

keywords_ai = KeywordsAITelemetry(
    app_name="multi-llm",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "test-key"))

anthropic_client = None
try:
    from anthropic import Anthropic
    anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"))
except ImportError:
    pass


@task(name="openai_call")
async def openai_call(prompt: str) -> str:
    """Call OpenAI."""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"Error: {e}"


@task(name="anthropic_call")
async def anthropic_call(prompt: str) -> str:
    """Call Anthropic."""
    if not anthropic_client:
        return "Anthropic not installed"
    try:
        resp = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text if resp.content else ""
    except Exception as e:
        return f"Error: {e}"


@task(name="combine")
async def combine(a: str, b: str) -> str:
    """Combine results."""
    return f"OpenAI: {a[:30]}... | Anthropic: {b[:30]}..."


@workflow(name="multi_llm_workflow")
async def multi_llm_workflow(prompt: str) -> dict:
    """Query multiple LLM providers."""
    client = get_client()
    if client:
        client.update_current_span(
            keywordsai_params={
                "customer_identifier": "multi_llm_user",
                "metadata": {"prompt": prompt},
            }
        )

    openai_result = await openai_call(prompt)
    anthropic_result = await anthropic_call(prompt)
    combined = await combine(openai_result, anthropic_result)

    return {"openai": openai_result, "anthropic": anthropic_result, "combined": combined}


async def main():
    print("=" * 50)
    print("Multi-LLM Provider Demo")
    print("=" * 50)
    print("Hierarchy: multi_llm_workflow -> openai_call, anthropic_call, combine\n")

    try:
        result = await multi_llm_workflow("Say hello briefly.")
        print(f"OpenAI: {result['openai']}")
        print(f"Anthropic: {result['anthropic']}")
    finally:
        keywords_ai.flush()
        await asyncio.sleep(2)

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
