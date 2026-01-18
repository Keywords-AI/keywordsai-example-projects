#!/usr/bin/env python3
"""
Basic Usage Example - KeywordsAI Tracing SDK

Demonstrates core SDK features:
- Decorators: @workflow, @task, @agent, @tool
- Client API: get_client(), update_current_span(), add_event(), record_exception()
- KeywordsAI params: customer_identifier, thread_identifier, metadata

Based on: https://github.com/Keywords-AI/keywordsai/blob/main/python-sdks/keywordsai-tracing/README.md
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task, agent, tool
from keywordsai_tracing.instruments import Instruments

# =============================================================================
# Initialize KeywordsAI Telemetry
# =============================================================================

keywords_ai = KeywordsAITelemetry(
    app_name="basic-usage-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),  # Or set KEYWORDSAI_API_KEY env var
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,  # Sync export for demo
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},  # Reduce noise
)


# =============================================================================
# @tool - Utility functions used by agents
# =============================================================================

@tool(name="search_database")
def search_database(query: str) -> dict:
    """Search tool - demonstrates tool decorator and span updates."""
    client = get_client()
    
    if client:
        # Add custom attributes to span
        client.update_current_span(
            attributes={
                "tool.type": "database",
                "tool.query": query,
            },
        )
        client.add_event("search.started", {"query_length": len(query)})
    
    # Simulate search
    results = {"matches": 3, "query": query}
    
    if client:
        client.add_event("search.completed", {"match_count": results["matches"]})
    
    return results


@tool(name="format_response")
def format_response(data: dict, style: str = "plain") -> str:
    """Formatter tool - can be sync or async."""
    client = get_client()
    
    if client:
        client.update_current_span(
            attributes={"formatter.style": style},
        )
    
    return f"[{style.upper()}] {data}"


# =============================================================================
# @task - Individual processing steps
# =============================================================================

@task(name="validate_input")
def validate_input(user_input: str) -> bool:
    """Task to validate user input."""
    client = get_client()
    
    if client:
        client.update_current_span(
            attributes={
                "validation.input_length": len(user_input),
                "validation.type": "text",
            },
        )
    
    is_valid = len(user_input.strip()) > 0
    
    if client:
        client.add_event("validation.result", {"is_valid": is_valid})
    
    return is_valid


@task(name="process_query")
async def process_query(query: str) -> str:
    """Async task to process a query."""
    client = get_client()
    
    if client:
        client.add_event("processing.started")
    
    await asyncio.sleep(0.1)  # Simulate processing
    result = f"Processed: {query}"
    
    if client:
        client.add_event("processing.completed", {"result_length": len(result)})
    
    return result


# =============================================================================
# @agent - Autonomous AI agents that use tools
# =============================================================================

@agent(name="research_agent")
async def research_agent(topic: str) -> dict:
    """Agent that uses tools to research a topic."""
    client = get_client()
    
    if client:
        # Set KeywordsAI-specific parameters
        client.update_current_span(
            keywordsai_params={
                "customer_identifier": "demo_user",
                "metadata": {"agent_type": "research", "topic": topic},
            },
        )
        client.add_event("agent.started", {"topic": topic})
    
    # Agent uses tools
    search_results = search_database(topic)
    formatted = format_response(search_results, style="json")
    
    if client:
        client.add_event("agent.completed")
    
    return {
        "topic": topic,
        "results": search_results,
        "formatted": formatted,
    }


# =============================================================================
# @workflow - Orchestrates tasks and agents
# =============================================================================

@workflow(name="main_workflow")
async def main_workflow(user_query: str) -> dict:
    """
    Main workflow demonstrating the full hierarchy:
    workflow -> task -> agent -> tool
    """
    client = get_client()
    
    if client:
        # Set workflow-level KeywordsAI parameters
        client.update_current_span(
            keywordsai_params={
                "customer_identifier": "basic_usage_demo_user",
                "thread_identifier": f"session_{os.getpid()}",
                "metadata": {
                    "workflow_type": "basic_demo",
                    "user_query": user_query,
                },
            },
        )
        client.add_event("workflow.started", {"query": user_query})
    
    # Step 1: Validate input (task)
    is_valid = validate_input(user_query)
    if not is_valid:
        return {"error": "Invalid input"}
    
    # Step 2: Process query (async task)
    processed = await process_query(user_query)
    
    # Step 3: Research with agent
    research = await research_agent(user_query)
    
    result = {
        "query": user_query,
        "processed": processed,
        "research": research,
        "status": "success",
    }
    
    if client:
        client.add_event("workflow.completed", {"status": "success"})
    
    return result


# =============================================================================
# Exception Handling Example
# =============================================================================

@task(name="risky_task")
async def risky_task(should_fail: bool = False) -> str:
    """Task demonstrating exception recording."""
    client = get_client()
    
    if client:
        client.add_event("risky_task.started", {"should_fail": should_fail})
    
    if should_fail:
        error = ValueError("Intentional failure for demo")
        if client:
            client.record_exception(error)
        raise error
    
    return "Success!"


# =============================================================================
# Main
# =============================================================================

async def main():
    """Run the basic usage demo."""
    print("=" * 60)
    print("KeywordsAI Tracing SDK - Basic Usage Demo")
    print("=" * 60)
    print("\nThis demo shows:")
    print("  - @workflow, @task, @agent, @tool decorators")
    print("  - get_client() for span manipulation")
    print("  - update_current_span() with attributes & keywordsai_params")
    print("  - add_event() for span events")
    print("  - record_exception() for error tracking")
    print("=" * 60)
    
    try:
        # Run main workflow
        print("\n[1/2] Running main workflow...")
        result = await main_workflow("What is machine learning?")
        print(f"Result: {result['status']}")
        
        # Demonstrate exception handling
        print("\n[2/2] Running risky task (success case)...")
        safe_result = await risky_task(should_fail=False)
        print(f"Safe result: {safe_result}")
        
        print("\n" + "=" * 60)
        print("Demo completed!")
        print("=" * 60)
        print("\nExpected trace hierarchy in KeywordsAI dashboard:")
        print("  main_workflow (workflow)")
        print("  +-- validate_input (task)")
        print("  +-- process_query (task)")
        print("  +-- research_agent (agent)")
        print("      +-- search_database (tool)")
        print("      +-- format_response (tool)")
        print("  risky_task (task)")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        print("\nFlushing traces...")
        keywords_ai.flush()
        await asyncio.sleep(1)
    
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
