#!/usr/bin/env python3
"""
Instrumentation Operations - KeywordsAI Tracing SDK
Demonstrates: instruments config, noise filtering, manual spans
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments

# Block HTTP noise, keep LLM provider instrumentation
keywords_ai = KeywordsAITelemetry(
    app_name="instrumentation-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


def show_config_patterns():
    """Show instrumentation configuration patterns."""
    print("""
Instrumentation Patterns:
  1. Default: all instruments enabled
  2. Whitelist: instruments={Instruments.OPENAI}
  3. Block noise: block_instruments={Instruments.REQUESTS, Instruments.URLLIB3}
  4. Manual only: instruments=set()
""")


async def demo_manual_spans():
    """Demonstrate manual span creation."""
    client = get_client()
    if not client:
        return

    tracer = client.get_tracer()

    # Basic manual span
    with tracer.start_as_current_span("manual_parent") as parent:
        parent.set_attribute("custom", True)
        parent.add_event("started")
        
        with tracer.start_as_current_span("manual_child") as child:
            child.set_attribute("level", 2)
            await asyncio.sleep(0.05)
        
        parent.add_event("completed")
    print("  Created nested manual spans")

    # Manual span with client API
    with tracer.start_as_current_span("combined_span"):
        client.update_current_span(
            attributes={"combined": True},
            keywordsai_params={"customer_identifier": "manual_user"},
        )
        client.add_event("combined.event")
    print("  Created span with client API")

    # Exception recording
    with tracer.start_as_current_span("error_span") as span:
        try:
            raise ValueError("Simulated error")
        except ValueError as e:
            span.record_exception(e)
            span.set_attribute("recovered", True)
    print("  Recorded exception (recovered)")


@task(name="filtered_task")
async def filtered_task():
    """Task with HTTP noise filtered out."""
    await asyncio.sleep(0.05)
    return {"data": "clean"}


@workflow(name="filtered_workflow")
async def filtered_workflow():
    """Workflow demonstrating clean traces."""
    data = await filtered_task()
    return data


async def main():
    print("=" * 50)
    print("Instrumentation Operations Demo")
    print("=" * 50)

    try:
        show_config_patterns()
        
        print("Manual span creation...")
        await demo_manual_spans()
        
        print("\nFiltered workflow...")
        result = await filtered_workflow()
        print(f"  Result: {result}")
    finally:
        keywords_ai.flush()
        await asyncio.sleep(1)

    print("\nAPIs: instruments, block_instruments, get_tracer(), start_as_current_span()")
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
