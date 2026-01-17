#!/usr/bin/env python3
"""
Instrumentation Management Example - KeywordsAI Tracing SDK

Demonstrates different ways to configure and manage instrumentations.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.instruments import Instruments


def run_instrumentation_demo():
    """Demonstrate different instrumentation configurations."""
    print("=== KeywordsAI Instrumentation Management Demo ===\n")
    
    # Example 1: Auto-discovery with disabled instrumentations
    print("1. Auto-discovery with disabled instrumentations:")
    auto_discovery_client = KeywordsAITelemetry(
        app_name="auto-discovery-demo",
        api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
        base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
        # Use block_instruments to disable specific instrumentations
        block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
    )
    print("Auto-discovery client initialized\n")
    
    # Example 2: Explicit module configuration
    print("2. Explicit module configuration:")
    explicit_client = KeywordsAITelemetry(
        app_name="explicit-modules-demo",
        api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
        base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
        # Use instruments to enable only specific modules
        instruments={Instruments.OPENAI},
    )
    print("Explicit client initialized\n")
    
    # Example 3: Custom instrumentation
    print("3. Custom module configuration:")
    
    class MyCustomInstrumentation:
        """Example custom instrumentation class."""
        def manually_instrument(self, module):
            print("Custom instrumentation logic applied to module!")
    
    custom_client = KeywordsAITelemetry(
        app_name="custom-module-demo",
        api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
        base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
        block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
    )
    print("Custom module client initialized\n")
    
    # Example 4: Environment-based configuration
    print("4. Environment-based configuration:")
    print(f"   KEYWORDSAI_API_KEY: {'***' + os.getenv('KEYWORDSAI_API_KEY', 'not-set')[-4:] if os.getenv('KEYWORDSAI_API_KEY') else 'not-set'}")
    print(f"   KEYWORDSAI_BASE_URL: {os.getenv('KEYWORDSAI_BASE_URL', 'not-set')}")
    print()
    
    print("Instrumentation management demo completed.")


if __name__ == "__main__":
    run_instrumentation_demo()
