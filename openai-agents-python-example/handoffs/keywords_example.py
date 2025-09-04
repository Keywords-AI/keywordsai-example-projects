from __future__ import annotations

import asyncio
import os
from agents import Agent, Runner, function_tool, trace
from agents.tracing import set_trace_processors
from keywordsai_processors import KeywordsProcessor

def setup_keywords_processor(endpoint: str = "https://api.keywordsai.co/api/"):
    """
    Set up the Keywords AI processor with the specified endpoint.
    
    Args:
        endpoint: The endpoint URL to use for exporting spans.
    """
    # Get API key from environment variable or use a default for testing
    api_key = os.environ.get("KEYWORDS_API_KEY", "your-api-key")
    
    # Create the processor
    processor = KeywordsProcessor(
        api_key=api_key,
        endpoint=endpoint,
        max_retries=3,
        schedule_delay=5.0,
    )
    
    # Set it as the only processor
    set_trace_processors([processor])
    
    return processor

@function_tool
def hello_world() -> str:
    """Return a hello world message."""
    return "Hello, World!"

async def run_example(endpoint: str):
    """
    Run a simple example using the specified endpoint.
    
    Args:
        endpoint: The endpoint URL to use for exporting spans.
    """
    # Set up the processor with the specified endpoint
    processor = setup_keywords_processor(endpoint)
    
    # Create a simple agent
    agent = Agent(
        name="Example Agent",
        instructions="You are a helpful assistant.",
        tools=[hello_world],
    )
    
    # Trace the workflow
    with trace(workflow_name=f"Keywords AI Example - {endpoint}"):
        print(f"Running example with endpoint: {endpoint}")
        
        # Run the agent
        result = await Runner.run(agent, input="Say hello!")
        
        print(f"Agent response: {result.content}")
    
    print(f"Traces exported to: {endpoint}")
    
    # Wait a bit to ensure all traces are exported
    await asyncio.sleep(6)

async def main():
    """Run examples with different endpoints."""
    # Example 1: Using the default API endpoint
    await run_example("https://api.keywordsai.co/api/")
    
    # Example 2: Using the alternative endpoint
    await run_example("https://endpoint.keywordsai.co/api/")
    
    # Example 3: Dynamically changing the endpoint
    processor = setup_keywords_processor("https://api.keywordsai.co/api/")
    
    with trace(workflow_name="Keywords AI Example - Dynamic Change"):
        print("Running example with dynamic endpoint change")
        
        # Create a simple agent
        agent = Agent(
            name="Example Agent",
            instructions="You are a helpful assistant.",
            tools=[hello_world],
        )
        
        # Run the agent
        result = await Runner.run(agent, input="Say hello!")
        
        print(f"Agent response: {result.content}")
        
        # Change the endpoint mid-workflow
        processor.set_endpoint("https://endpoint.keywordsai.co/api/")
        print("Endpoint changed to: https://endpoint.keywordsai.co/api/")
        
        # Run the agent again
        result = await Runner.run(agent, input="Say hello again!")
        
        print(f"Agent response: {result.content}")
    
    print("All examples completed")

if __name__ == "__main__":
    asyncio.run(main()) 