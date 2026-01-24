#!/usr/bin/env python3
"""
Span Operations - KeywordsAI Tracing SDK
Demonstrates: span buffering, events, exceptions, keywordsai_params
"""
import os
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from opentelemetry.semconv_ai import SpanAttributes
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

    input_attributes = {
        SpanAttributes.TRACELOOP_ENTITY_INPUT: json.dumps({
            "args": [],
            "kwargs": {"text": "Record events and exceptions."}
        }),
    }
    client.update_current_span(attributes=input_attributes)

    client.add_event("started")
    try:
        raise ValueError("Demo error")
    except ValueError as e:
        client.record_exception(e)
    client.add_event("completed")

    result = {
        "status": "completed",
        "events": ["started", "completed"],
        "exception": "ValueError: Demo error",
    }
    client.update_current_span(
        attributes={
            SpanAttributes.TRACELOOP_ENTITY_OUTPUT: json.dumps(result),
        }
    )
    return result


@workflow(name="span_management")
async def demo_span_management():
    """Span management features."""
    print("\n[2] Span Management")
    client = get_client()
    if not client:
        return

    input_attributes = {
        SpanAttributes.TRACELOOP_ENTITY_INPUT: json.dumps({
            "args": [],
            "kwargs": {"text": "Manage spans: step 1."}
        }),
        "step": 1,
    }

    client.update_current_span(
        name="span_management.active",
        attributes=input_attributes,
        keywordsai_params={"metadata": {"step": 1}},
    )
    client.add_event("checkpoint", {"n": 1})
    
    events_result = demo_events()
    print("  Events and exceptions recorded")

    # Manual spans
    tracer = client.get_tracer()
    with tracer.start_as_current_span("manual") as span:
        span.set_attribute("manual", True)
    print("  Manual span created")

    result = {
        "status": "ok",
        "events": events_result,
        "manual_span": True,
    }
    client.update_current_span(
        attributes={
            SpanAttributes.TRACELOOP_ENTITY_OUTPUT: json.dumps(result),
        }
    )
    return result


@agent(name="params_agent")
async def demo_keywordsai_params():
    """KeywordsAI-specific parameters."""
    print("\n[3] KeywordsAI Params")
    client = get_client()
    if not client:
        return ""

    client.update_current_span(
        attributes={
            SpanAttributes.TRACELOOP_ENTITY_INPUT: json.dumps({
                "args": [],
                "kwargs": {"text": "Set KeywordsAI customer and model params."}
            }),
        }
    )

    customer_params = {
        "customer_identifier": "user_123",
        "thread_identifier": "conv_456",
        "metadata": {"version": "2.0"},
    }
    client.update_current_span(keywordsai_params=customer_params)
    print("  Customer params set")

    # LLM params
    llm_params = {
        "model": "gpt-4",
        "prompt_tokens": 50,
        "completion_tokens": 100,
        "cost": 0.003,
    }
    client.update_current_span(keywordsai_params=llm_params)
    print("  LLM params set")
    result = {
        "status": "done",
        "customer_identifier": "user_123",
        "thread_identifier": "conv_456",
        "model": "gpt-4",
        "prompt_tokens": 50,
        "completion_tokens": 100,
        "cost": 0.003,
    }
    token_usage = {
        SpanAttributes.LLM_USAGE_PROMPT_TOKENS: llm_params["prompt_tokens"],
        SpanAttributes.LLM_USAGE_COMPLETION_TOKENS: llm_params["completion_tokens"],
        SpanAttributes.LLM_USAGE_TOTAL_TOKENS: llm_params["prompt_tokens"] + llm_params["completion_tokens"],
    }
    client.update_current_span(
        attributes={
            SpanAttributes.TRACELOOP_ENTITY_OUTPUT: json.dumps(result),
            **token_usage,
        },
        keywordsai_params={**customer_params, **llm_params, "log_type": "generation"},
    )
    return result


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
