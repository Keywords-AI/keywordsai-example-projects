#!/usr/bin/env python3
"""
Span Operations Example - KeywordsAI Tracing SDK

Comprehensive example covering all span-related operations:
1. Span buffering with get_span_buffer()
2. Span management (update, events, exceptions)
3. KeywordsAI params (customer_identifier, metadata, model info)
4. Manual span creation with get_tracer()

Documentation: https://github.com/Keywords-AI/keywordsai/blob/main/python-sdks/keywordsai-tracing/README.md
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task, agent
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry
keywords_ai = KeywordsAITelemetry(
    app_name="span-operations-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)


# =============================================================================
# PART 1: Span Buffering
# =============================================================================

def demo_span_buffering():
    """Demonstrate span buffering with get_span_buffer()."""
    print("\n" + "=" * 50)
    print("PART 1: Span Buffering")
    print("=" * 50)
    
    client = get_client()
    if not client:
        print("Error: Could not get client")
        return
    
    # Create spans in a buffer
    print("\n1.1 Creating spans in buffer...")
    collected_spans = []
    
    with client.get_span_buffer("trace-123") as buffer:
        buffer.create_span("step_1", {"status": "completed", "duration_ms": 100})
        buffer.create_span("step_2", {"status": "completed", "duration_ms": 200})
        buffer.create_span("step_3", {"status": "completed", "duration_ms": 150})
        
        print(f"    Buffered {buffer.get_span_count()} spans")
        collected_spans = buffer.get_all_spans()
    
    # Conditional processing
    print("\n1.2 Conditional span processing...")
    should_export = True
    if should_export:
        success = client.process_spans(collected_spans)
        print(f"    Processing {'succeeded' if success else 'failed'}")
    else:
        print("    Spans discarded (not processed)")
    
    # Create spans from workflow results
    print("\n1.3 Creating spans from workflow results...")
    results = [
        {"name": "task_a", "latency": 100, "success": True},
        {"name": "task_b", "latency": 150, "success": True},
    ]
    
    with client.get_span_buffer("experiment-456") as buffer:
        for r in results:
            buffer.create_span(r["name"], {"latency_ms": r["latency"], "success": r["success"]})
        print(f"    Created {buffer.get_span_count()} spans from results")
        client.process_spans(buffer.get_all_spans())


# =============================================================================
# PART 2: Span Management (Events, Exceptions, Manual Spans)
# =============================================================================

@task(name="task_with_events")
def demo_events_and_exceptions():
    """Demonstrate adding events and recording exceptions."""
    client = get_client()
    if not client:
        return
    
    # Add events
    client.add_event("processing.started", {"source": "cache"})
    
    # Record an exception (but continue)
    try:
        raise ValueError("Simulated error for demo")
    except ValueError as e:
        client.record_exception(e)
        print("    Exception recorded (but handled)")
    
    client.add_event("processing.completed", {"records": 42})


@task(name="task_with_manual_spans")
def demo_manual_spans():
    """Demonstrate manual span creation with get_tracer()."""
    client = get_client()
    if not client:
        return
    
    tracer = client.get_tracer()
    
    # Create manual spans
    with tracer.start_as_current_span("manual_parent") as parent:
        parent.set_attribute("manual", True)
        parent.add_event("parent.started")
        
        with tracer.start_as_current_span("manual_child") as child:
            child.set_attribute("level", 2)
            print("    Created nested manual spans")


@workflow(name="span_management_workflow")
async def demo_span_management():
    """Demonstrate span management features."""
    print("\n" + "=" * 50)
    print("PART 2: Span Management")
    print("=" * 50)
    
    client = get_client()
    if not client:
        print("Error: Could not get client")
        return
    
    # Get trace/span IDs
    print("\n2.1 Getting trace/span IDs...")
    try:
        print(f"    Trace ID: {client.get_current_trace_id()}")
        print(f"    Span ID: {client.get_current_span_id()}")
    except AttributeError:
        print("    ID methods not available")
    
    # Update span attributes
    print("\n2.2 Updating span attributes...")
    client.update_current_span(
        name="span_management.processing",
        attributes={"status": "processing", "step": 1}
    )
    print("    Span updated")
    
    # Add events
    print("\n2.3 Adding events...")
    client.add_event("workflow.checkpoint", {"checkpoint": 1})
    await asyncio.sleep(0.05)
    client.add_event("workflow.checkpoint", {"checkpoint": 2})
    print("    Events added")
    
    # Events and exceptions in sub-task
    print("\n2.4 Events and exception recording...")
    demo_events_and_exceptions()
    
    # Manual spans
    print("\n2.5 Manual span creation...")
    demo_manual_spans()
    
    # Get current span
    print("\n2.6 Inspecting current span...")
    span = client.get_current_span()
    print(f"    Current span exists: {span is not None}")


# =============================================================================
# PART 3: KeywordsAI Parameters
# =============================================================================

@task(name="llm_call_with_params")
async def demo_llm_params():
    """Demonstrate LLM-specific KeywordsAI parameters."""
    client = get_client()
    if not client:
        return "no client"
    
    client.update_current_span(
        keywordsai_params={
            "model": "gpt-4",
            "provider": "openai",
            "temperature": 0.7,
            "prompt_tokens": 50,
            "completion_tokens": 150,
            "cost": 0.003,
        },
        attributes={"llm.type": "chat_completion"}
    )
    
    await asyncio.sleep(0.05)
    return "LLM response"


@agent(name="agent_with_params")
async def demo_keywordsai_params():
    """Demonstrate KeywordsAI-specific parameters."""
    print("\n" + "=" * 50)
    print("PART 3: KeywordsAI Parameters")
    print("=" * 50)
    
    client = get_client()
    if not client:
        print("Error: Could not get client")
        return {}
    
    # Customer identification
    print("\n3.1 Customer identification...")
    client.update_current_span(
        keywordsai_params={
            "customer_identifier": "user_123",
            "customer_email": "user@example.com",
            "thread_identifier": "conversation_456",
        }
    )
    print("    Customer params added")
    
    # Metadata
    print("\n3.2 Metadata...")
    client.update_current_span(
        keywordsai_params={
            "metadata": {
                "experiment": "A/B-test-v1",
                "version": "2.0.0",
                "environment": "staging",
            }
        }
    )
    print("    Metadata added")
    
    # LLM parameters in sub-task
    print("\n3.3 LLM parameters...")
    result = await demo_llm_params()
    print(f"    LLM task completed: {result}")
    
    # Final status
    print("\n3.4 Final status update...")
    client.update_current_span(
        name="agent_with_params.completed",
        attributes={"completed": True, "success": True}
    )
    print("    Agent completed")
    
    return {"status": "completed"}


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Run all span operation demos."""
    print("=" * 60)
    print("Span Operations Demo - KeywordsAI Tracing SDK")
    print("=" * 60)
    
    try:
        # Part 1: Span Buffering (sync)
        demo_span_buffering()
        
        # Part 2: Span Management (async workflow)
        await demo_span_management()
        
        # Part 3: KeywordsAI Parameters (async agent)
        await demo_keywordsai_params()
        
    except Exception as e:
        print(f"\nError: {e}")
        raise
    finally:
        # Flush all pending spans before exit
        print("\nFlushing traces...")
        keywords_ai.flush()
    
    print("\n" + "=" * 60)
    print("All span operations demos completed!")
    print("=" * 60)
    print("\nAPIs demonstrated:")
    print("  - get_span_buffer() / process_spans()")
    print("  - update_current_span()")
    print("  - add_event() / record_exception()")
    print("  - get_tracer() / start_as_current_span()")
    print("  - keywordsai_params: customer_identifier, metadata, model, cost, etc.")


if __name__ == "__main__":
    asyncio.run(main())
