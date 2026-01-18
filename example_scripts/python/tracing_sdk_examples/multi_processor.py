#!/usr/bin/env python3
"""
Multi-Processor Example - KeywordsAI Tracing SDK

Demonstrates routing spans to multiple destinations using add_processor().
Shows how to use the 'processors' parameter in decorators for selective routing.

Based on: https://github.com/Keywords-AI/keywordsai/blob/main/python-sdks/keywordsai-tracing/README.md#multiple-processors-routing-spans

Key Concepts:
- Default processor: automatically sends to KeywordsAI when api_key is provided
- add_processor(): adds additional processors with automatic filtering by name
- processors parameter: routes spans to specific processors (single or list)
"""
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Sequence
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments


# =============================================================================
# Custom Exporters (for demonstration)
# In production, use: ConsoleSpanExporter, OTLPSpanExporter, etc.
# =============================================================================

class FileExporter(SpanExporter):
    """
    Custom file exporter that writes spans to a JSONL file.
    Implements the OpenTelemetry SpanExporter interface.
    """
    
    def __init__(self, filepath: str, name: str = "file"):
        self.filepath = filepath
        self.name = name
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        # Clear file on init
        with open(filepath, "w") as f:
            f.write("")
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to file."""
        try:
            with open(self.filepath, "a") as f:
                for span in spans:
                    span_data = {
                        "name": span.name,
                        "trace_id": format(span.context.trace_id, "032x") if span.context else None,
                        "span_id": format(span.context.span_id, "016x") if span.context else None,
                        "attributes": dict(span.attributes) if span.attributes else {},
                        "exported_at": datetime.now().isoformat(),
                        "exporter": self.name,
                    }
                    f.write(json.dumps(span_data) + "\n")
            return SpanExportResult.SUCCESS
        except Exception as e:
            print(f"  [FileExporter:{self.name}] Export error: {e}")
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


class ConsoleExporter(SpanExporter):
    """Simple console exporter for debugging."""
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        for span in spans:
            print(f"  [{self.prefix}] Span: {span.name}")
        return SpanExportResult.SUCCESS
    
    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


# =============================================================================
# Initialize KeywordsAI Telemetry
# =============================================================================

# Default processor is automatically added when api_key is provided
keywords_ai = KeywordsAITelemetry(
    app_name="multi-processor-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


# =============================================================================
# Add Custom Processors
# =============================================================================

# Add processors for different routing destinations
# The 'name' parameter enables automatic filtering via processors="name"

# Debug processor - writes to file for local debugging
keywords_ai.add_processor(
    exporter=FileExporter("./output/debug-spans.jsonl", name="debug"),
    name="debug"  # Spans with processors="debug" go here
)

# Analytics processor - writes to separate file for analytics
keywords_ai.add_processor(
    exporter=FileExporter("./output/analytics-spans.jsonl", name="analytics"),
    name="analytics"  # Spans with processors="analytics" go here
)

print("Processors configured:")
print("  - default: KeywordsAI (automatic)")
print("  - debug: ./output/debug-spans.jsonl")
print("  - analytics: ./output/analytics-spans.jsonl")


# =============================================================================
# Tasks with Different Processor Routing
# =============================================================================

@task(name="normal_task")
async def normal_task():
    """
    Normal task - goes to default KeywordsAI processor only.
    No processors parameter = uses default.
    """
    client = get_client()
    if client:
        client.update_current_span(
            attributes={"task.type": "normal", "task.routing": "default"},
        )
        client.add_event("task.executed")
    
    await asyncio.sleep(0.05)
    return "normal_result"


@task(name="debug_task", processors="debug")
async def debug_task():
    """
    Debug task - routed to debug processor only.
    Uses processors="debug" for single processor routing.
    """
    client = get_client()
    if client:
        client.update_current_span(
            attributes={
                "task.type": "debug",
                "task.routing": "debug",
                "debug.verbose": True,
                "debug.level": "trace",
            },
        )
        client.add_event("debug.checkpoint", {"step": 1, "state": "running"})
    
    await asyncio.sleep(0.05)
    
    if client:
        client.add_event("debug.checkpoint", {"step": 2, "state": "completed"})
    
    return "debug_result"


@task(name="analytics_task", processors="analytics")
async def analytics_task():
    """
    Analytics task - routed to analytics processor only.
    Uses processors="analytics" for single processor routing.
    """
    client = get_client()
    if client:
        client.update_current_span(
            attributes={
                "task.type": "analytics",
                "task.routing": "analytics",
                "analytics.metric": "user_engagement",
                "analytics.value": 0.85,
            },
        )
        client.add_event("analytics.recorded", {"records_processed": 42})
    
    await asyncio.sleep(0.08)
    return "analytics_result"


@task(name="multi_destination_task", processors=["debug", "analytics"])
async def multi_destination_task():
    """
    Multi-destination task - routes to BOTH debug and analytics processors.
    Uses processors=["debug", "analytics"] for multiple routing.
    """
    client = get_client()
    if client:
        client.update_current_span(
            attributes={
                "task.type": "multi",
                "task.routing": "debug,analytics",
                "multi.reason": "important_event",
            },
        )
        client.add_event("multi.started")
    
    await asyncio.sleep(0.1)
    
    if client:
        client.add_event("multi.completed", {"status": "success"})
    
    return "multi_result"


# =============================================================================
# Main Workflow
# =============================================================================

@workflow(name="multi_processor_workflow")
async def run_multi_processor_demo():
    """
    Workflow demonstrating multi-processor routing.
    
    Routing summary:
    - normal_task: default (KeywordsAI)
    - debug_task: debug processor only
    - analytics_task: analytics processor only
    - multi_destination_task: debug + analytics
    """
    client = get_client()
    if client:
        client.update_current_span(
            keywordsai_params={
                "customer_identifier": "multi_processor_demo_user",
                "thread_identifier": f"thread_{os.getpid()}",
            },
        )
    
    results = {}
    
    # 1. Normal task - default processor (KeywordsAI)
    print("\n[1/4] Normal Task (default -> KeywordsAI)")
    results["normal"] = await normal_task()
    
    # 2. Debug task - debug processor only
    print("[2/4] Debug Task (debug -> debug-spans.jsonl)")
    results["debug"] = await debug_task()
    
    # 3. Analytics task - analytics processor only
    print("[3/4] Analytics Task (analytics -> analytics-spans.jsonl)")
    results["analytics"] = await analytics_task()
    
    # 4. Multi-destination task - multiple processors
    print("[4/4] Multi-Destination Task (debug + analytics)")
    results["multi"] = await multi_destination_task()
    
    return results


async def main():
    """Run the multi-processor demo."""
    print("=" * 60)
    print("Multi-Processor Routing Demo - KeywordsAI Tracing SDK")
    print("=" * 60)
    print("\nThis demo shows how to route spans to different destinations:")
    print("  - No processors param -> default KeywordsAI processor")
    print("  - processors='name' -> single named processor")
    print("  - processors=['a','b'] -> multiple processors")
    print("=" * 60)
    
    try:
        results = await run_multi_processor_demo()
        
        print("\n--- Results ---")
        for key, value in results.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        print("\nFlushing traces...")
        keywords_ai.flush()
        await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print("Demo completed. Check output files:")
    print("  - ./output/debug-spans.jsonl (debug + multi_destination)")
    print("  - ./output/analytics-spans.jsonl (analytics + multi_destination)")
    print("  - KeywordsAI dashboard (normal_task + workflow)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
