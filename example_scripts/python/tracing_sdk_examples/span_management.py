#!/usr/bin/env python3
"""
Span Management Example - KeywordsAI Tracing SDK

Using the get_client() API to manually update spans, add events, and record exceptions.
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

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="span-management-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)


@task(name="sub_task")
def run_sub_task():
    """A sub-task that demonstrates event recording and exception handling."""
    print("In sub-task...")
    
    client = get_client()
    
    # Add an event to the sub-task
    if client:
        client.add_event("sub_task_event")
    
    # Simulate and record an exception
    print("Recording a simulated exception...")
    try:
        raise ValueError("Something went wrong in the sub-task")
    except ValueError as e:
        if client:
            client.record_exception(e)


@workflow(name="main_workflow")
async def run_span_management_demo():
    """Main workflow demonstrating span management features."""
    client = get_client()
    
    # Get current trace/span IDs if available
    if client:
        try:
            trace_id = client.get_current_trace_id()
            span_id = client.get_current_span_id()
            print(f"Trace ID: {trace_id}")
            print(f"Span ID: {span_id}")
        except AttributeError:
            print("Trace/span ID methods not available in this SDK version")
    
    # Update span attributes
    print("Updating span attributes...")
    if client:
        client.update_current_span(
            name="main_workflow.executed",
            attributes={
                "custom.status": "processing",
                "env": "test"
            },
            keywordsai_params={
                "customer_identifier": "user_999",
                "metadata": {
                    "version": "2.0.0"
                }
            }
        )
    
    # Add an event
    print("Adding an event...")
    if client:
        client.add_event("data_fetch_started", {
            "source": "cache",
            "priority": "high"
        })
    
    await asyncio.sleep(0.2)
    
    # Run sub-task
    run_sub_task()
    
    # Add workflow completion event
    if client:
        client.add_event("workflow_completed")


async def main():
    """Run the span management demo."""
    print("Starting Span Management Demo\n")
    
    try:
        await run_span_management_demo()
    except Exception as e:
        print(f"Error: {e}")
        raise
    
    print("\nSpan management demo completed.")


if __name__ == "__main__":
    asyncio.run(main())
