#!/usr/bin/env python3
"""
OpenAI Integration Example - KeywordsAI Tracing SDK

Demonstrates automatic instrumentation of the OpenAI SDK with KeywordsAI tracing.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from openai import OpenAI
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import workflow
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="openai-integration-test",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "test-api-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)

# Initialize OpenAI client (using KeywordsAI proxy if OPENAI_BASE_URL is set)
openai_base_url = os.getenv("OPENAI_BASE_URL")
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "test-api-key"),
    base_url=openai_base_url if openai_base_url else None,
)
print(f"OpenAI base URL: {openai_base_url or 'default'}")


@workflow(name="openai_chat_completion")
def run_openai_integration_test():
    """Run OpenAI integration test with KeywordsAI tracing."""
    print("Starting OpenAI Integration Test with KeywordsAI\n")
    
    try:
        print("Sending request to OpenAI...")
        
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me a short joke about programming."}
            ],
        )
        
        print("OpenAI Response:", completion.choices[0].message.content)
        return completion.choices[0].message.content
        
    except Exception as e:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "test-api-key" or api_key.startswith("your_"):
            print("Skipping real API call (no valid OPENAI_API_KEY found).")
            print("In a real scenario, the instrumentation would capture the request and response automatically.")
            return "Simulated response"
        else:
            raise e


def main():
    """Main entry point."""
    print("KeywordsAI initialized successfully\n")
    
    try:
        result = run_openai_integration_test()
        print(f"\nCleaning up...")
        print("Done!")
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
