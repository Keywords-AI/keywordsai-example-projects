#!/usr/bin/env python3
"""
Basic Usage - KeywordsAI Tracing SDK
Demonstrates: @workflow, @task, @agent, @tool decorators + client API
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task, agent, tool
from keywordsai_tracing.instruments import Instruments

keywords_ai = KeywordsAITelemetry(
    app_name="basic-usage",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


@tool(name="search_db")
def search_db(query: str) -> dict:
    """Tool: utility function used by agents."""
    client = get_client()
    if client:
        client.update_current_span(attributes={"query": query})
        client.add_event("search.done", {"matches": 3})
    return {"matches": 3, "query": query}


@task(name="validate")
def validate(text: str) -> bool:
    """Task: individual processing step."""
    client = get_client()
    if client:
        client.add_event("validated", {"length": len(text)})
    return len(text.strip()) > 0


@agent(name="research_agent")
async def research_agent(topic: str) -> dict:
    """Agent: uses tools to accomplish goals."""
    client = get_client()
    if client:
        client.update_current_span(
            keywordsai_params={"customer_identifier": "demo_user", "metadata": {"topic": topic}}
        )
    results = search_db(topic)
    return {"topic": topic, "results": results}


@workflow(name="main_workflow")
async def main_workflow(query: str) -> dict:
    """Workflow: orchestrates tasks and agents."""
    client = get_client()
    if client:
        client.update_current_span(
            keywordsai_params={
                "customer_identifier": "basic_demo_user",
                "thread_identifier": f"session_{os.getpid()}",
            }
        )
        client.add_event("workflow.started")

    if not validate(query):
        return {"error": "Invalid input"}

    research = await research_agent(query)
    
    if client:
        client.add_event("workflow.completed")
    return {"query": query, "research": research, "status": "success"}


@task(name="risky_task")
def risky_task(fail: bool = False) -> str:
    """Demonstrates exception recording."""
    client = get_client()
    if fail:
        error = ValueError("Intentional failure")
        if client:
            client.record_exception(error)
        raise error
    return "Success"


async def main():
    print("=" * 50)
    print("Basic Usage Demo")
    print("=" * 50)

    try:
        result = await main_workflow("machine learning")
        print(f"Result: {result['status']}")
        
        safe = risky_task(fail=False)
        print(f"Risky task: {safe}")
    finally:
        keywords_ai.flush()
        await asyncio.sleep(1)

    print("\nExpected hierarchy:")
    print("  main_workflow -> validate -> research_agent -> search_db")
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
