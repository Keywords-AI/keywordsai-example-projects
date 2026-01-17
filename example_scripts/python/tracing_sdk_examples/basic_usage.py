#!/usr/bin/env python3
"""
Basic Usage Example - KeywordsAI Tracing SDK

Core concepts: workflow, task, agent, tool decorators and context managers.
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task, agent, tool
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="basic-example",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)


@task(name="generate_response", version=1)
async def generate_response(prompt: str) -> str:
    """Generate a response for a given prompt."""
    await asyncio.sleep(0.1)  # Simulate processing
    return f"Response to: {prompt}"


@workflow(name="chat_workflow", version=1)
async def chat_workflow(user_message: str) -> str:
    """A simple chat workflow demonstrating task composition."""
    response = await generate_response(user_message)
    
    @task(name="log_interaction")
    def log_interaction():
        print(f"User: {user_message}")
        print(f"Assistant: {response}")
        return "logged"
    
    log_interaction()
    return response


@tool(name="query_analyzer")
def query_analyzer(query: str) -> dict:
    """Analyze a query to determine intent and complexity."""
    return {
        "intent": "question" if "?" in query else "statement",
        "length": len(query),
        "complexity": "high" if len(query.split()) > 10 else "low"
    }


@tool(name="response_generator")
async def response_generator(analysis: dict) -> str:
    """Generate a response based on query analysis."""
    await asyncio.sleep(0.1)  # Simulate processing
    return f"Response based on analysis: {analysis}"


@agent(name="assistant_agent")
async def assistant_agent(query: str) -> dict:
    """An assistant agent that analyzes queries and generates responses."""
    analysis = query_analyzer(query)
    response = await response_generator(analysis)
    
    return {
        "analysis": analysis,
        "response": response
    }


async def main():
    """Run all basic usage examples."""
    try:
        print("=== Basic Task Example ===")
        basic_response = await generate_response("Hello, how are you?")
        print("Response:", basic_response)
        
        print("\n=== Workflow Example ===")
        workflow_response = await chat_workflow("What is the weather like?")
        print("Workflow Response:", workflow_response)
        
        print("\n=== Agent Example ===")
        agent_response = await assistant_agent("Can you explain quantum computing?")
        print("Agent Response:", agent_response)
        
        print("\n=== All examples completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
