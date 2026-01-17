#!/usr/bin/env python3
"""
Comprehensive Usage Example - KeywordsAI Tracing SDK

Comprehensive example using all utility functions: get_client, update_current_span,
add_span_event, record_span_exception, set_span_status, and all decorators.
"""
import os
import asyncio
import random
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import workflow, task, tool, agent
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="my-ai-app",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)


# Example 1: Using decorators for automatic tracing
@task(name="summarize")
async def summarize(text: str) -> str:
    """Summarize the given text."""
    client = get_client()
    
    if client:
        client.update_current_span(
            attributes={
                "document.length": len(text),
                "document.type": "text",
            },
        )
        client.add_event("summarization.started", {
            "model": "gpt-4",
            "max_tokens": 150,
        })
    
    await asyncio.sleep(0.1)
    
    return f"Summary of: {text[:50]}..."


@tool(name="validate-summary")
def validate_summary(summary: str) -> bool:
    """Validate the summary length."""
    client = get_client()
    
    if len(summary) < 10:
        error = ValueError("Summary too short")
        if client:
            client.record_exception(error)
            from opentelemetry.trace import StatusCode
            client.update_current_span(status=StatusCode.ERROR, status_description="Summary validation failed")
        raise error
    
    if client:
        from opentelemetry.trace import StatusCode
        client.update_current_span(status=StatusCode.OK)
    
    return True


@workflow(name="document-processing")
async def process_document(document: str) -> dict:
    """Process a document by summarizing and validating."""
    print("Processing document:", document[:50] + "...")
    
    summary = await summarize(document)
    is_valid = validate_summary(summary)
    
    return {"summary": summary, "is_valid": is_valid}


# Example 2: Agent-based processing
@tool(name="retrieve-context")
def retrieve_context(query: str) -> str:
    """Retrieve context for the given query."""
    client = get_client()
    
    if client:
        client.update_current_span(
            attributes={
                "search.query": query,
                "search.type": "semantic",
            },
        )
    
    return f"Context for: {query}"


@tool(name="generate-response")
async def generate_response(context: str) -> str:
    """Generate a response based on context."""
    client = get_client()
    
    if client:
        client.add_event("llm.call.started", {
            "model": "gpt-4",
            "temperature": 0.7,
        })
    
    await asyncio.sleep(0.2)
    
    if client:
        client.add_event("llm.call.completed", {
            "tokens.used": 150,
            "cost.usd": 0.003,
        })
    
    return f"AI Response based on: {context}"


@agent(name="customer-support-agent", version=1)
async def ai_agent(user_query: str) -> str:
    """AI agent that retrieves context and generates responses."""
    context = retrieve_context(user_query)
    response = await generate_response(context)
    return response


# Example 3: Error handling
@workflow(name="risky-operation")
def error_prone_operation() -> dict:
    """An operation that might fail randomly."""
    client = get_client()
    
    if client:
        try:
            span = client.get_current_span()
            if span:
                print(f"Current span: {span.get_span_context().span_id if hasattr(span, 'get_span_context') else 'N/A'}")
        except Exception:
            pass
        print(f"SDK initialized: {client is not None}")
    
    random_value = random.random()
    if random_value < 0.3:
        raise RuntimeError("Random failure occurred")
    
    if client:
        client.update_current_span(
            attributes={
                "operation.success": True,
                "random.value": random_value,
            },
        )
    
    return {"success": True, "value": random_value}


async def main():
    """Run all usage examples."""
    print("Initializing KeywordsAI tracing...\n")
    print("Tracing initialized\n")
    
    try:
        print("=== Document Processing Example ===")
        result1 = await process_document(
            "This is a sample document that needs to be processed and summarized."
        )
        print("Result:", result1)
        
        print("\n=== AI Agent Example ===")
        result2 = await ai_agent("How can I reset my password?")
        print("Result:", result2)
        
        print("\n=== Error Handling Example ===")
        for i in range(3):
            try:
                result3 = error_prone_operation()
                print(f"Attempt {i + 1} succeeded:", result3)
                break
            except RuntimeError as e:
                print(f"Attempt {i + 1} failed:", str(e))
        
    except Exception as e:
        print(f"Main execution failed: {e}")
        raise
    
    print("\nAll examples completed.")


if __name__ == "__main__":
    asyncio.run(main())
    print("\nExample completed. Check your KeywordsAI dashboard for traces!")
