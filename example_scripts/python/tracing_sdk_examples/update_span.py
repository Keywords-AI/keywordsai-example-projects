#!/usr/bin/env python3
"""
Update Span Example - KeywordsAI Tracing SDK

Advanced span updating with KeywordsAI-specific parameters.
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry, get_client
from keywordsai_tracing.decorators import agent
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="update-span-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)


@agent(name="advancedAgent")
async def run_update_span_demo() -> dict:
    """Demonstrate advanced span updating with KeywordsAI parameters."""
    print("Agent started...")
    
    client = get_client()
    
    # Update span with KeywordsAI-specific parameters
    print("Updating span with KeywordsAI parameters...")
    if client:
        client.update_current_span(
            keywordsai_params={
                "model": "gpt-4",
                "provider": "openai",
                "temperature": 0.7,
                "max_tokens": 1000,
                "user_id": "user123",
                "metadata": {
                    "experiment": "A/B-test-v1",
                    "feature_flag": "new_ui_enabled",
                },
            },
            attributes={
                "custom.operation": "llm_call",
                "custom.priority": "high",
            },
        )
    
    await asyncio.sleep(0.1)
    
    # Update span name and processing stage
    print("Updating span name and processing stage...")
    if client:
        client.update_current_span(
            name="advancedAgent.processing",
            attributes={
                "processing.stage": "analysis",
            },
        )
    
    # Mark span as completed
    print("Marking span as completed...")
    if client:
        client.update_current_span(
            attributes={
                "processing.stage": "completed",
                "result.count": 42,
            },
        )
    
    return {
        "result": "Advanced processing completed",
        "processed_items": 42,
        "model_used": "gpt-4",
    }


async def main():
    """Run the update span demo."""
    print("Starting Update Span Demo\n")
    
    try:
        result = await run_update_span_demo()
        print(f"\nResult: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    
    print("\nUpdate span demo completed.")


if __name__ == "__main__":
    asyncio.run(main())
