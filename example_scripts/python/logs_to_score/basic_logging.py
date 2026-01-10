#!/usr/bin/env python3
"""
Basic Logging Example

This example demonstrates the basic logging functionality as shown in the
KeywordsAI quickstart guide.

Quickstart guide: https://docs.keywordsai.co/get-started/quickstart/logging
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
API_KEY = os.getenv("KEYWORDSAI_API_KEY")


def create_log(
    model: str,
    input_messages: List[Dict[str, str]],
    output_message: Dict[str, str],
    custom_identifier: Optional[str] = None,
    span_name: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new log entry in Keywords AI.
    
    Args:
        model: Model name (e.g., "gpt-4o", "claude-3-5-sonnet")
        input_messages: List of input messages in OpenAI format
        output_message: Output message in OpenAI format
        custom_identifier: Optional custom identifier for the log
        span_name: Optional span name for the log
        **kwargs: Additional fields to include in the log
    
    Returns:
        Dict containing the created log data
    """
    url = f"{BASE_URL}/request-logs/create"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": model,
        "input": input_messages,
        "output": output_message
    }
    
    if custom_identifier:
        payload["custom_identifier"] = custom_identifier
    if span_name:
        payload["span_name"] = span_name
    
    # Add any additional fields
    payload.update(kwargs)
    
    print("Creating log entry...")
    print(f"  URL: {url}")
    print(f"  Model: {model}")
    print(f"  Input messages: {len(input_messages)}")
    if custom_identifier:
        print(f"  Custom identifier: {custom_identifier}")
    if span_name:
        print(f"  Span name: {span_name}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Log created successfully")
    if 'unique_id' in data:
        print(f"  Log ID (unique_id): {data.get('unique_id')}")
    if 'id' in data:
        print(f"  Log ID: {data.get('id')}")
    if 'trace_id' in data:
        print(f"  Trace ID: {data.get('trace_id')}")
    
    return data


def main():
    """Example usage of basic logging."""
    print("=" * 80)
    print("KeywordsAI Basic Logging Example")
    print("=" * 80)
    
    # Example 1: Simple log entry
    print("\n📝 Example 1: Creating a simple log entry")
    print("-" * 80)
    
    log_data = create_log(
        model="gpt-4o",
        input_messages=[
            {"role": "user", "content": "What is the capital of France?"}
        ],
        output_message={
            "role": "assistant",
            "content": "The capital of France is Paris."
        }
    )
    
    # Example 2: Log with custom identifier
    print("\n📝 Example 2: Creating a log with custom identifier")
    print("-" * 80)
    
    log_data_2 = create_log(
        model="gpt-4o-mini",
        input_messages=[
            {"role": "user", "content": "Tell me a fun fact about space"}
        ],
        output_message={
            "role": "assistant",
            "content": "A day on Venus is longer than its year! Venus rotates so slowly that it takes longer to complete one rotation than to orbit the Sun once."
        },
        custom_identifier="space_fact_query_001"
    )
    
    # Example 3: Log with span name
    print("\n📝 Example 3: Creating a log with span name")
    print("-" * 80)
    
    log_data_3 = create_log(
        model="claude-3-5-sonnet-20241022",
        input_messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms"}
        ],
        output_message={
            "role": "assistant",
            "content": "Quantum computing uses quantum mechanical phenomena like superposition and entanglement to perform computations. Unlike classical bits that are either 0 or 1, quantum bits (qubits) can exist in multiple states simultaneously, allowing for parallel processing of information."
        },
        span_name="quantum_explanation"
    )
    
    # Example 4: Multi-turn conversation
    print("\n📝 Example 4: Creating a log for multi-turn conversation")
    print("-" * 80)
    
    log_data_4 = create_log(
        model="gpt-4o",
        input_messages=[
            {"role": "user", "content": "What's the weather like?"},
            {"role": "assistant", "content": "I don't have access to real-time weather data. Could you tell me your location?"},
            {"role": "user", "content": "San Francisco"}
        ],
        output_message={
            "role": "assistant",
            "content": "I still can't access real-time weather, but I'd recommend checking a weather app or website like Weather.com for current conditions in San Francisco."
        },
        custom_identifier="weather_conversation_001",
        span_name="weather_assistant"
    )
    
    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
    
    return {
        "log_1": log_data,
        "log_2": log_data_2,
        "log_3": log_data_3,
        "log_4": log_data_4
    }


if __name__ == "__main__":
    main()
