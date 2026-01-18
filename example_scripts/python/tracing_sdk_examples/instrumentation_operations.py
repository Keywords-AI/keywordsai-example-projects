#!/usr/bin/env python3
"""
Manual Instrumentation Example - KeywordsAI Tracing SDK

Comprehensive example covering:
1. Instrumentation configuration (instruments, block_instruments)
2. Noise filtering (blocking HTTP library spans)
3. Manual span creation with get_tracer()

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
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments


# =============================================================================
# PART 1: Instrumentation Configuration Reference
# =============================================================================

def show_instrumentation_configs():
    """Show different instrumentation configuration patterns."""
    print("\n" + "=" * 50)
    print("PART 1: Instrumentation Configuration")
    print("=" * 50)
    
    print("""
Available Instruments:
  Instruments.OPENAI       - OpenAI SDK calls
  Instruments.ANTHROPIC    - Anthropic SDK calls
  Instruments.REQUESTS     - requests library HTTP calls
  Instruments.URLLIB3      - urllib3 HTTP calls
  Instruments.THREADING    - Thread context propagation

Configuration Patterns:

1. Default (all instruments enabled):
   KeywordsAITelemetry(app_name="app", api_key=key)

2. Whitelist specific instruments:
   KeywordsAITelemetry(
       app_name="app",
       api_key=key,
       instruments={Instruments.OPENAI},  # Only OpenAI
   )

3. Block noisy instruments (recommended):
   KeywordsAITelemetry(
       app_name="app",
       api_key=key,
       block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
   )

4. Manual only (no auto-instrumentation):
   KeywordsAITelemetry(
       app_name="app",
       api_key=key,
       instruments=set(),  # Empty set
   )
""")


# =============================================================================
# PART 2: Noise Filtering Explanation
# =============================================================================

def show_noise_filtering():
    """Explain noise filtering with block_instruments."""
    print("\n" + "=" * 50)
    print("PART 2: Noise Filtering")
    print("=" * 50)
    
    print("""
WITHOUT noise filtering (noisy traces):
  workflow: my_workflow
  +-- task: fetch_data
  |   +-- requests: GET https://api.example.com   <- noise
  |       +-- urllib3: request                    <- noise
  +-- task: call_llm
  |   +-- openai: chat_completions                <- useful
  |       +-- requests: POST https://api.openai   <- noise
  |           +-- urllib3: request                <- noise

WITH block_instruments (clean traces):
  workflow: my_workflow
  +-- task: fetch_data
  +-- task: call_llm
      +-- openai: chat_completions                <- useful

Recommendation for production:
  block_instruments={Instruments.REQUESTS, Instruments.URLLIB3}
""")


# =============================================================================
# Initialize telemetry with noise filtering
# =============================================================================

keywords_ai = KeywordsAITelemetry(
    app_name="manual-instrumentation-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    # Block noisy HTTP instruments, keep LLM providers
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


# =============================================================================
# PART 3: Manual Span Creation
# =============================================================================

async def demo_manual_spans():
    """Demonstrate manual span creation with get_tracer()."""
    print("\n" + "=" * 50)
    print("PART 3: Manual Span Creation")
    print("=" * 50)
    
    client = get_client()
    if not client:
        print("Error: Could not get client")
        return
    
    tracer = client.get_tracer()
    
    # 3.1 Basic manual span
    print("\n3.1 Basic manual span...")
    with tracer.start_as_current_span("manual_parent") as parent:
        parent.set_attribute("custom.operation", "demo")
        parent.add_event("started")
        
        # Nested child span
        with tracer.start_as_current_span("manual_child") as child:
            child.set_attribute("level", 2)
            await asyncio.sleep(0.05)
        
        parent.add_event("completed")
    print("    Created parent with nested child span")
    
    # 3.2 Manual span with KeywordsAI client
    print("\n3.2 Manual span with KeywordsAI client...")
    with tracer.start_as_current_span("combined_span"):
        client.update_current_span(
            attributes={"combined": True},
            keywordsai_params={
                "customer_identifier": "manual_user",
                "metadata": {"type": "manual"},
            },
        )
        client.add_event("combined.event")
        await asyncio.sleep(0.05)
    print("    Created span with client methods")
    
    # 3.3 Deep nesting
    print("\n3.3 Deep nesting...")
    with tracer.start_as_current_span("level_0"):
        with tracer.start_as_current_span("level_1"):
            with tracer.start_as_current_span("level_2"):
                with tracer.start_as_current_span("level_3") as deepest:
                    deepest.add_event("deepest_point")
    print("    Created 4 levels of nested spans")
    
    # 3.4 Exception recording
    print("\n3.4 Exception recording...")
    with tracer.start_as_current_span("error_span") as span:
        try:
            raise ValueError("Simulated error")
        except ValueError as e:
            span.record_exception(e)
            span.set_attribute("recovered", True)
    print("    Recorded exception (span continues)")
    
    # 3.5 Parallel spans
    print("\n3.5 Parallel spans...")
    
    async def parallel_task(name: str):
        with tracer.start_as_current_span(f"parallel_{name}") as span:
            span.set_attribute("name", name)
            await asyncio.sleep(0.05)
            return name
    
    with tracer.start_as_current_span("parallel_parent"):
        results = await asyncio.gather(
            parallel_task("a"),
            parallel_task("b"),
            parallel_task("c"),
        )
    print(f"    Created parallel spans: {results}")


# =============================================================================
# PART 4: Practical Workflow with Filtered Instrumentation
# =============================================================================

@task(name="fetch_data")
async def fetch_data():
    """Fetch data - HTTP spans filtered out."""
    await asyncio.sleep(0.05)
    return {"items": [1, 2, 3]}


@task(name="process_data")
def process_data(data: dict):
    """Process data."""
    return {"count": len(data.get("items", []))}


@workflow(name="filtered_workflow")
async def demo_filtered_workflow():
    """Workflow demonstrating clean traces with noise filtering."""
    print("\n" + "=" * 50)
    print("PART 4: Filtered Workflow Demo")
    print("=" * 50)
    
    print("\nRunning workflow with block_instruments active...")
    print("  (HTTP spans are filtered out)\n")
    
    data = await fetch_data()
    print(f"    fetch_data: {data}")
    
    result = process_data(data)
    print(f"    process_data: {result}")
    
    return result


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Run all instrumentation demos."""
    print("=" * 60)
    print("Manual Instrumentation Demo - KeywordsAI Tracing SDK")
    print("=" * 60)
    
    try:
        # Part 1: Show configuration reference
        show_instrumentation_configs()
        
        # Part 2: Explain noise filtering
        show_noise_filtering()
        
        # Part 3: Manual span creation
        await demo_manual_spans()
        
        # Part 4: Filtered workflow
        await demo_filtered_workflow()
        
    except Exception as e:
        print(f"\nError: {e}")
        raise
    finally:
        # Flush all pending spans before exit
        print("\nFlushing traces...")
        keywords_ai.flush()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
APIs demonstrated:
  - instruments={...}       Whitelist specific auto-instrumentations
  - block_instruments={...} Block noisy instrumentations
  - get_tracer()            Get OpenTelemetry tracer for manual spans
  - start_as_current_span() Create manual spans with context manager
  - span.set_attribute()    Set span attributes
  - span.add_event()        Add events to spans
  - span.record_exception() Record exceptions on spans
""")


if __name__ == "__main__":
    asyncio.run(main())
