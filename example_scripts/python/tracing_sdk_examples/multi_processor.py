#!/usr/bin/env python3
"""
Multi-Processor / Span Tracking & Logging Example - KeywordsAI Tracing SDK

This example demonstrates span tracking and custom logging:
1. Tracking different types of tasks (normal, debug, analytics, slow)
2. Adding custom attributes and events
3. Logging span information to files and console
4. Demonstrating workflow with multiple task types
"""
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="span-tracking-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)


def log_span_to_file(filepath: str, span_info: dict):
    """Log span information to a file."""
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(span_info) + "\n")
        print(f"  Logged to {filepath}")
    except Exception as e:
        print(f"  File logging error: {e}")


def log_span_to_console(prefix: str, span_info: dict):
    """Log span information to console."""
    print(f"  [{prefix}] {span_info['name']} - {span_info['type']}")


@task(name="normal_task")
async def normal_task():
    """A normal task with standard tracing."""
    client = get_client()
    
    if client:
        client.update_current_span(
            attributes={
                "task.type": "normal",
                "task.priority": "medium",
            },
        )
        client.add_event("task.started", {"timestamp": datetime.now().isoformat()})
    
    await asyncio.sleep(0.05)
    
    if client:
        client.add_event("task.completed", {"timestamp": datetime.now().isoformat()})
    
    print("  Completed (standard tracing)")


@task(name="debug_task")
async def debug_task():
    """A debug task with file logging."""
    client = get_client()
    start_time = datetime.now()
    
    if client:
        client.update_current_span(
            attributes={
                "task.type": "debug",
                "task.priority": "low",
                "debug.enabled": True,
            },
        )
        client.add_event("debug.started", {"level": "verbose"})
    
    await asyncio.sleep(0.05)
    
    span_info = {
        "name": "debug_task",
        "type": "debug",
        "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
        "timestamp": datetime.now().isoformat(),
    }
    
    log_span_to_file("./debug-spans.jsonl", span_info)
    
    if client:
        client.add_event("debug.logged", {"file": "debug-spans.jsonl"})
    
    print("  Completed (logged to file)")


@task(name="analytics_task")
async def analytics_task():
    """An analytics task with console and file logging."""
    client = get_client()
    start_time = datetime.now()
    
    if client:
        client.update_current_span(
            attributes={
                "task.type": "analytics",
                "task.priority": "high",
                "analytics.enabled": True,
            },
        )
        client.add_event("analytics.started", {"metrics": "enabled"})
    
    await asyncio.sleep(0.08)
    
    span_info = {
        "name": "analytics_task",
        "type": "analytics",
        "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
        "metrics": {"processed": 42, "errors": 0},
        "timestamp": datetime.now().isoformat(),
    }
    
    log_span_to_console("Analytics", span_info)
    log_span_to_file("./analytics-spans.jsonl", span_info)
    
    if client:
        client.add_event("analytics.completed", {"records": 42})
    
    print("  Completed (logged to console & file)")


@task(name="slow_task")
async def slow_task():
    """A slow task demonstrating long-running operation tracking."""
    client = get_client()
    start_time = datetime.now()
    
    if client:
        client.update_current_span(
            attributes={
                "task.type": "slow",
                "task.priority": "low",
                "performance.warning": True,
            },
        )
        client.add_event("slow.task.started", {"expected_duration": "200ms"})
    
    await asyncio.sleep(0.2)
    
    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    span_info = {
        "name": "slow_task",
        "type": "slow",
        "duration_ms": duration_ms,
        "warning": "Exceeded threshold" if duration_ms > 100 else None,
        "timestamp": datetime.now().isoformat(),
    }
    
    log_span_to_console("SlowSpans", span_info)
    log_span_to_file("./slow-spans.jsonl", span_info)
    
    if client:
        client.add_event("slow.task.completed", {"actual_duration_ms": duration_ms})
    
    print(f"  Completed in {duration_ms:.0f}ms (performance logged)")


@workflow(name="span_tracking_workflow")
async def run_multi_processor_demo():
    """Run a workflow with multiple task types."""
    # Normal task - standard tracing
    print("1. Normal Task:")
    await normal_task()
    
    # Debug task - with debug logging
    print("\n2. Debug Task:")
    await debug_task()
    
    # Analytics task - with console analytics
    print("\n3. Analytics Task:")
    await analytics_task()
    
    # Slow task - demonstrates long-running operation
    print("\n4. Slow Task (long-running):")
    await slow_task()


async def main():
    """Run the multi-processor demo."""
    print("Starting Span Tracking & Logging Demo\n")
    
    try:
        await run_multi_processor_demo()
    except Exception as e:
        print(f"Error: {e}")
        raise
    
    print("\nSpan tracking demo completed.")
    print("\nCheck these files for logged spans:")
    print("   - ./debug-spans.jsonl")
    print("   - ./analytics-spans.jsonl")
    print("   - ./slow-spans.jsonl")


if __name__ == "__main__":
    asyncio.run(main())
