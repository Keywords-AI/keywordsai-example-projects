#!/usr/bin/env python3
"""
Noise Filtering Example - KeywordsAI Tracing SDK

Demonstrates how the SDK filters out auto-instrumentation noise
(like pure HTTP calls) outside of user contexts.
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task, tool
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="noise-filtering-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)

# Initialize OpenAI client (using KeywordsAI proxy if OPENAI_BASE_URL is set)
openai_base_url = os.getenv("OPENAI_BASE_URL")
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "test-key"),
    base_url=openai_base_url if openai_base_url else None,
)


@task(name="llm_task")
def llm_task():
    """A task that makes an OpenAI call inside a workflow context."""
    print("    Making OpenAI call inside task...")
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print(f"    OpenAI response: {response.choices[0].message.content or 'N/A'}")
        print("    This openai.chat span should be a CHILD of llm_task\n")
        return response.choices[0].message.content
    except Exception as e:
        print(f"    OpenAI call failed: {e}\n")
        return "Simulated response"


@task(name="another_llm_task")
def another_llm_task():
    """Another task that makes an OpenAI call."""
    print("    Making another OpenAI call...")
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Count to 3"}],
            max_tokens=15
        )
        print(f"    OpenAI response: {response.choices[0].message.content or 'N/A'}")
        print("    This openai.chat span should be a CHILD of another_llm_task\n")
        return response.choices[0].message.content
    except Exception as e:
        print(f"    OpenAI call failed: {e}\n")
        return "Simulated response"


@tool(name="utility_tool")
async def utility_tool():
    """A utility tool that doesn't make LLM calls."""
    print("    Running utility tool (no LLM call)...")
    await asyncio.sleep(0.05)
    print("    Utility completed\n")


@workflow(name="noise_filtered_workflow")
async def noise_filtered_workflow():
    """A workflow that contains multiple tasks and tools."""
    print("  Inside workflow context...\n")
    
    llm_task()
    another_llm_task()
    await utility_tool()


async def run_noise_filtering_demo():
    """Run the noise filtering demonstration."""
    print("=== KeywordsAI Noise Filtering Demo ===\n")
    
    # Scenario 1: OpenAI request OUTSIDE any context
    print("Scenario 1: Making an OpenAI request OUTSIDE any context")
    print("(This should NOT be sent to KeywordsAI - filtered as noise)\n")
    try:
        openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        print("  OpenAI call completed (but span should be filtered)\n")
    except Exception:
        print("  OpenAI call failed or simulated\n")
    
    # Scenario 2: OpenAI requests INSIDE a workflow context
    print("Scenario 2: Making OpenAI requests INSIDE a workflow context")
    print("(Child spans SHOULD be preserved and sent to KeywordsAI)\n")
    
    await noise_filtered_workflow()
    
    # Print expected trace structure
    print("Noise filtering demo completed.")
    print("\nExpected trace structure:")
    print("   noise_filtered_workflow (workflow)")
    print("   +-- llm_task (task)")
    print("   |   +-- openai.chat (child span - PRESERVED)")
    print("   +-- another_llm_task (task)")
    print("   |   +-- openai.chat (child span - PRESERVED)")
    print("   +-- utility_tool (tool)")
    print("\n   Scenario 1 openai.chat span: FILTERED (not in trace)")


async def main():
    """Run the noise filtering demo."""
    try:
        await run_noise_filtering_demo()
    except Exception as e:
        print(f"Error: {e}")
        raise
    
    print("\nDemo complete.")


if __name__ == "__main__":
    asyncio.run(main())
