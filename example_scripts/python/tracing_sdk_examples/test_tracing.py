#!/usr/bin/env python3
"""
Test Tracing - KeywordsAI Tracing SDK

Comprehensive test with a multi-step workflow (joke creation, translation, signature generation).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="pirate-joke-test",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    is_batching_enabled=False,
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)

# Initialize OpenAI client (using KeywordsAI proxy if OPENAI_BASE_URL is set)
openai_base_url = os.getenv("OPENAI_BASE_URL")
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "test-key"),
    base_url=openai_base_url if openai_base_url else None,
)


@task(name="joke_creation")
def create_joke() -> str:
    """Create a joke about OpenTelemetry."""
    print("Task: Creating joke...")
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Tell me a short joke about OpenTelemetry"}],
            temperature=0.7
        )
        return completion.choices[0].message.content or ""
    except Exception:
        print("  (Simulated joke creation)")
        return "Why did the OpenTelemetry span cross the road? To trace the other side!"


@task(name="pirate_joke_translation")
def translate_to_pirate(joke: str) -> str:
    """Translate the joke to pirate language."""
    print("Task: Translating to pirate...")
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Translate this joke to pirate language: {joke}"}],
            temperature=0.7
        )
        return completion.choices[0].message.content or ""
    except Exception:
        print("  (Simulated pirate translation)")
        return f"Arrr! {joke}"


@task(name="signature_generation")
def generate_signature(pirate_joke: str) -> str:
    """Generate a pirate signature for the joke."""
    print("Task: Generating signature...")
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Add a creative pirate signature to this joke: {pirate_joke}"}],
            temperature=0.7
        )
        return completion.choices[0].message.content or ""
    except Exception:
        print("  (Simulated signature generation)")
        return f"{pirate_joke}\n\n- Captain Tracebeard"


@workflow(name="joke_workflow")
def pirate_joke_workflow() -> str:
    """Complete workflow for creating a pirate joke."""
    print("Starting Pirate Joke Workflow...")
    
    # Task 1: Joke Creation
    joke = create_joke()
    
    # Task 2: Pirate Translation
    pirate_joke = translate_to_pirate(joke)
    
    # Task 3: Signature Generation
    signature_joke = generate_signature(pirate_joke)
    
    return signature_joke


def main():
    """Run the test tracing example."""
    print("Starting KeywordsAI tracing test...")
    print("SDK initialized\n")
    
    try:
        final_result = pirate_joke_workflow()
        
        print("\n--- Final Result ---")
        print(final_result)
        print("--------------------")
        
        print("\nTest completed successfully")
        
    except Exception as e:
        print(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
