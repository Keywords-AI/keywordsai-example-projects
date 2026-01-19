#!/usr/bin/env python3
"""
Span Operations - KeywordsAI Tracing SDK
Demonstrates: span buffering, events, exceptions, keywordsai_params
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task, agent
from keywordsai_tracing.instruments import Instruments

keywords_ai = KeywordsAITelemetry(
    app_name="span-operations",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


def demo_span_buffering():
    """Span buffering with get_span_buffer()."""
    print("\n[1] Span Buffering")
    client = get_client()
    if not client:
        return

    collected = []
    with client.get_span_buffer("trace-123") as buffer:
        buffer.create_span("step_1", {"status": "done"})
        buffer.create_span("step_2", {"status": "done"})
        print(f"  Buffered {buffer.get_span_count()} spans")
        collected = buffer.get_all_spans()

    client.process_spans(collected)
    print("  Processed spans")


@task(name="events_demo")
def demo_events():
    """Events and exceptions."""
    client = get_client()
    if not client:
        return

    client.add_event("started")
    try:
        raise ValueError("Demo error")
    except ValueError as e:
        client.record_exception(e)
    client.add_event("completed")


@workflow(name="span_management")
async def demo_span_management():
    """Span management features."""
    print("\n[2] Span Management")
    client = get_client()
    if not client:
        return

    client.update_current_span(
        name="span_management.active",
        attributes={"step": 1}
    )
    client.add_event("checkpoint", {"n": 1})
    
    demo_events()
    print("  Events and exceptions recorded")

    # Manual spans
    tracer = client.get_tracer()
    with tracer.start_as_current_span("manual") as span:
        span.set_attribute("manual", True)
    print("  Manual span created")


@agent(name="params_agent")
async def demo_keywordsai_params():
    """KeywordsAI-specific parameters."""
    print("\n[3] KeywordsAI Params")
    client = get_client()
    if not client:
        return {}

    client.update_current_span(
        keywordsai_params={
            "customer_identifier": "user_123",
            "thread_identifier": "conv_456",
            "metadata": {"version": "2.0"},
        }
    )
    print("  Customer params set")

    # LLM params
    client.update_current_span(
        keywordsai_params={
            "model": "gpt-4",
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "cost": 0.003,
        }
    )
    print("  LLM params set")
    return {"status": "done"}


async def main():
    print("=" * 50)
    print("Span Operations Demo")
    print("=" * 50)

    try:
        demo_span_buffering()
        await demo_span_management()
        await demo_keywordsai_params()
    finally:
        keywords_ai.flush()
        await asyncio.sleep(1)

    print("\nAPIs: get_span_buffer(), process_spans(), update_current_span(),")
    print("      add_event(), record_exception(), keywordsai_params")
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
