#!/usr/bin/env python3
"""
Advanced Tracing Example - KeywordsAI Tracing SDK

Agentic workflows with agent, tool decorators, and custom metadata.
"""
import os
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import agent, tool, task
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="advanced-tracing-example",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)

# Initialize OpenAI client (using KeywordsAI proxy if OPENAI_BASE_URL is set)
openai_base_url = os.getenv("OPENAI_BASE_URL")
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "test-api-key"),
    base_url=openai_base_url if openai_base_url else None,
)


@tool(name="query_analyzer")
async def analyze_query(query: str) -> dict:
    """Analyze the query to determine topic and sentiment."""
    print("Analyzing query...")
    await asyncio.sleep(0.3)  # Simulate processing
    return {
        "topic": "technology" if "ai" in query.lower() else "general",
        "sentiment": "neutral"
    }


@tool(name="web_search")
def web_search(topic: str) -> str:
    """Simulate a web search for information."""
    print("Searching the web...")
    return f"Found some information about {topic}"


@task(name="final_generation")
def generate_final_response(query: str, analysis: dict, search_results: str) -> str:
    """Generate the final response using OpenAI."""
    print("Generating final response...")
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a research assistant. Topic: {analysis['topic']}. Info: {search_results}"
                },
                {"role": "user", "content": query}
            ],
        )
        return completion.choices[0].message.content
    except Exception:
        return "Here is your simulated research result based on the analysis."


@agent(name="research_assistant")
async def run_agent_example(query: str) -> dict:
    """Run a research assistant agent that analyzes queries and generates responses."""
    print(f"Agent received query: {query}")
    
    # Analyze the query
    analysis = await analyze_query(query)
    
    # Search for information
    search_results = web_search(analysis["topic"])
    
    # Generate final response
    final_response = generate_final_response(query, analysis, search_results)
    
    return {
        "analysis": analysis,
        "search_results": search_results,
        "final_response": final_response
    }


async def main():
    """Run the advanced tracing example."""
    try:
        print("Starting Advanced Tracing Example\n")
        
        result = await run_agent_example("How is AI changing software development?")
        print("\nAgent Execution Result:", json.dumps(result, indent=2))
        
        print("\nExample completed.")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
