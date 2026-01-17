#!/usr/bin/env python3
"""
Create Log Scores Example

This example demonstrates how to create scores on logs using evaluators.
Scores link evaluators to specific log entries and store evaluation results.

Documentation: https://docs.keywordsai.co/api-endpoints/evaluate/log-scores/create
"""

import os
import requests
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
API_KEY = os.getenv("KEYWORDSAI_API_KEY")


def create_log_score(
    log_id: str,
    evaluator_slug: str,
    score: float,
    reasoning: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    score_type: str = "numerical"
) -> Dict[str, Any]:
    """
    Create a score on a specific log using an evaluator.
    
    Args:
        log_id: The unique ID of the log to score (use 'unique_id' from log creation)
        evaluator_slug: The slug of the evaluator to use
        score: The score value (can be float, str, bool, or list depending on score_type)
        reasoning: Optional reasoning/explanation for the score
        metadata: Optional metadata to attach to the score
        score_type: Type of score - "numerical", "string", "boolean", "categorical", or "json"
    
    Returns:
        Dict containing the created score data
    """
    url = f"{BASE_URL}/scores"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "log_id": log_id,
        "evaluator_slug": evaluator_slug
    }
    
    # Add the appropriate value field based on score_type
    if score_type == "numerical":
        payload["numerical_value"] = float(score)
    elif score_type == "string":
        payload["string_value"] = str(score)
    elif score_type == "boolean":
        payload["boolean_value"] = bool(score)
    elif score_type == "categorical":
        payload["categorical_value"] = score if isinstance(score, list) else [score]
    elif score_type == "json":
        payload["json_value"] = json.dumps(score) if not isinstance(score, str) else score
    else:
        # Default to numerical
        payload["numerical_value"] = float(score)
    
    if reasoning:
        payload["reasoning"] = reasoning
    if metadata:
        payload["metadata"] = metadata
    
    print("Creating log score...")
    print(f"  URL: {url}")
    print(f"  Log ID: {log_id}")
    print(f"  Evaluator Slug: {evaluator_slug}")
    print(f"  Score: {score}")
    if reasoning:
        print(f"  Reasoning: {reasoning[:100]}..." if len(reasoning) > 100 else f"  Reasoning: {reasoning}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Score created successfully")
    if 'id' in data:
        print(f"  Score ID: {data.get('id')}")
    # Check for different value types
    if 'numerical_value' in data and data.get('numerical_value') is not None:
        print(f"  Score Value (numerical): {data.get('numerical_value')}")
    elif 'string_value' in data and data.get('string_value'):
        print(f"  Score Value (string): {data.get('string_value')}")
    elif 'boolean_value' in data and data.get('boolean_value') is not None:
        print(f"  Score Value (boolean): {data.get('boolean_value')}")
    elif 'categorical_value' in data and data.get('categorical_value'):
        print(f"  Score Value (categorical): {data.get('categorical_value')}")
    
    return data


def create_log_score_batch(
    scores: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create multiple scores in a single batch request.
    
    Args:
        scores: List of score objects, each containing:
            - log_id: The log ID
            - evaluator_slug: The evaluator slug
            - score: The score value
            - reasoning: Optional reasoning
            - metadata: Optional metadata
    
    Returns:
        Dict containing batch creation results
    """
    url = f"{BASE_URL}/evaluate/log-scores/create-batch"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "scores": scores
    }
    
    print("Creating batch log scores...")
    print(f"  URL: {url}")
    print(f"  Number of scores: {len(scores)}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Batch scores created successfully")
    if 'created' in data:
        print(f"  Created: {data.get('created')}")
    if 'failed' in data:
        print(f"  Failed: {data.get('failed')}")
    
    return data


def main():
    """Example usage of log score creation."""
    print("=" * 80)
    print("KeywordsAI Create Log Scores Example")
    print("=" * 80)
    print("\n⚠️  Note: This example requires existing logs and evaluators.")
    print("   Please run basic_logging.py and create_evaluator.py first.\n")
    
    # Example 1: Create a single score
    print("📊 Example 1: Creating a single score on a log")
    print("-" * 80)
    print("\nTo create a score, you need:")
    print("  1. A log ID (from basic_logging.py or list_request_logs.py)")
    print("  2. An evaluator slug (from create_evaluator.py)")
    print("\nExample code:")
    print("-" * 80)
    
    example_code = """
    # Replace these with actual values from your account
    log_id = "your-log-unique-id-here"
    evaluator_slug = "response_quality"  # From create_evaluator.py
    
    score_data = create_log_score(
        log_id=log_id,
        evaluator_slug=evaluator_slug,
        score=0.85,
        reasoning="The response is accurate, relevant, and provides a complete answer to the user's question."
    )
    """
    print(example_code)
    
    # Example 2: Create score with metadata
    print("\n📊 Example 2: Creating a score with metadata")
    print("-" * 80)
    print("\nExample code:")
    print("-" * 80)
    
    example_code_2 = """
    score_data = create_log_score(
        log_id="your-log-unique-id-here",
        evaluator_slug="response_quality",
        score=0.92,
        reasoning="Excellent response with high accuracy and helpfulness.",
        metadata={
            "evaluated_by": "human_reviewer_001",
            "evaluation_date": "2024-01-15",
            "confidence": 0.95
        }
    )
    """
    print(example_code_2)
    
    # Example 3: Create batch scores
    print("\n📊 Example 3: Creating multiple scores in batch")
    print("-" * 80)
    print("\nExample code:")
    print("-" * 80)
    
    example_code_3 = """
    scores = [
        {
            "log_id": "log-id-1",
            "evaluator_slug": "response_quality",
            "score": 0.85,
            "reasoning": "Good response quality"
        },
        {
            "log_id": "log-id-2",
            "evaluator_slug": "response_quality",
            "score": 0.92,
            "reasoning": "Excellent response quality"
        },
        {
            "log_id": "log-id-1",
            "evaluator_slug": "factual_accuracy",
            "score": True,  # For boolean evaluators
            "reasoning": "No factual inaccuracies detected"
        }
    ]
    
    batch_result = create_log_score_batch(scores=scores)
    """
    print(example_code_3)
    
    # Example 4: Complete workflow example
    print("\n📊 Example 4: Complete workflow")
    print("-" * 80)
    print("\nThis shows the complete workflow:")
    print("  1. Create logs")
    print("  2. Create evaluators")
    print("  3. List logs to get log IDs")
    print("  4. Create scores on logs")
    print("-" * 80)
    
    workflow_code = """
    # Step 1: Create a log (from basic_logging.py)
    from basic_logging import create_log
    log_data = create_log(
        model="gpt-4o",
        input_messages=[{"role": "user", "content": "What is Python?"}],
        output_message={"role": "assistant", "content": "Python is a programming language..."},
        custom_identifier="python_question_001"
    )
    log_id = log_data.get('unique_id')
    
    # Step 2: Create an evaluator (from create_evaluator.py)
    from create_evaluator import create_llm_evaluator
    evaluator_data = create_llm_evaluator(
        name="Response Quality",
        evaluator_slug="response_quality",
        evaluator_definition="Evaluate response quality...",
        scoring_rubric="0.0=Poor, 1.0=Excellent"
    )
    evaluator_slug = evaluator_data.get('evaluator_slug')
    
    # Step 3: Create a score on the log
    from create_log_scores import create_log_score
    score_data = create_log_score(
        log_id=log_id,
        evaluator_slug=evaluator_slug,
        score=0.88,
        reasoning="The response accurately explains Python as a programming language."
    )
    """
    print(workflow_code)
    
    print("\n" + "=" * 80)
    print("Examples completed! Use these patterns with your actual log IDs and evaluator slugs.")
    print("=" * 80)


if __name__ == "__main__":
    main()
