#!/usr/bin/env python3
"""
Create Evaluator Example

This example demonstrates how to create custom evaluators in KeywordsAI.
Evaluators are used to automatically score and evaluate logs.

Documentation: https://docs.keywordsai.co/api-endpoints/evaluate/evaluators/create
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
API_KEY = os.getenv("KEYWORDSAI_API_KEY")

# Evaluator configuration from environment variables
EVALUATOR_LLM_ENGINE = os.getenv("EVALUATOR_LLM_ENGINE", "gpt-4o-mini")
EVALUATOR_TEMPERATURE = float(os.getenv("EVALUATOR_TEMPERATURE", "0.1"))
EVALUATOR_MAX_TOKENS = int(os.getenv("EVALUATOR_MAX_TOKENS", "200"))
DEFAULT_MIN_SCORE = float(os.getenv("DEFAULT_MIN_SCORE", "0.0"))
DEFAULT_MAX_SCORE = float(os.getenv("DEFAULT_MAX_SCORE", "1.0"))
DEFAULT_PASSING_SCORE = float(os.getenv("DEFAULT_PASSING_SCORE", "0.7"))


def create_evaluator(
    name: str,
    evaluator_slug: str,
    evaluator_type: str,
    score_value_type: str,
    description: str = "",
    configurations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a custom evaluator in Keywords AI.
    
    Args:
        name: Human-readable name for the evaluator
        evaluator_slug: Unique slug identifier (e.g., "response_quality")
        evaluator_type: Type of evaluator ("llm", "code", "custom", etc.)
        score_value_type: Type of score ("numerical", "boolean", "categorical")
        description: Optional description of the evaluator
        configurations: Optional configuration dict with evaluator-specific settings
    
    Returns:
        Dict containing the created evaluator data
    """
    url = f"{BASE_URL}/evaluators"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "name": name,
        "evaluator_slug": evaluator_slug,
        "type": evaluator_type,
        "score_value_type": score_value_type,
        "description": description
    }
    
    if configurations:
        payload["configurations"] = configurations
    
    print("Creating evaluator...")
    print(f"  URL: {url}")
    print(f"  Name: {name}")
    print(f"  Slug: {evaluator_slug}")
    print(f"  Type: {evaluator_type}")
    print(f"  Score Type: {score_value_type}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Evaluator created successfully")
    if 'id' in data:
        print(f"  Evaluator ID: {data.get('id')}")
    if 'evaluator_slug' in data:
        print(f"  Evaluator Slug: {data.get('evaluator_slug')}")
    
    return data


def create_llm_evaluator(
    name: str,
    evaluator_slug: str,
    evaluator_definition: str,
    scoring_rubric: str,
    description: str = "",
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    passing_score: Optional[float] = None,
    llm_engine: Optional[str] = None,
    model_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create an LLM-based evaluator with custom definition and scoring rubric.
    
    Args:
        name: Human-readable name for the evaluator
        evaluator_slug: Unique slug identifier
        evaluator_definition: Definition/prompt for the evaluator that uses {{input}} and {{output}}
        scoring_rubric: Description of the scoring rubric
        description: Optional description
        min_score: Minimum possible score
        max_score: Maximum possible score
        passing_score: Score threshold for passing
        llm_engine: LLM model to use for evaluation
        model_options: Optional model configuration (temperature, max_tokens, etc.)
    
    Returns:
        Dict containing the created evaluator data
    """
    # Use environment variables as defaults if not provided
    final_min_score = min_score if min_score is not None else DEFAULT_MIN_SCORE
    final_max_score = max_score if max_score is not None else DEFAULT_MAX_SCORE
    final_passing_score = passing_score if passing_score is not None else DEFAULT_PASSING_SCORE
    final_llm_engine = llm_engine if llm_engine is not None else EVALUATOR_LLM_ENGINE
    
    configurations = {
        "evaluator_definition": evaluator_definition,
        "scoring_rubric": scoring_rubric,
        "min_score": final_min_score,
        "max_score": final_max_score,
        "passing_score": final_passing_score,
        "llm_engine": final_llm_engine
    }
    
    if model_options:
        configurations["model_options"] = model_options
    
    return create_evaluator(
        name=name,
        evaluator_slug=evaluator_slug,
        evaluator_type="llm",
        score_value_type="numerical",
        description=description,
        configurations=configurations
    )


def main():
    """Example usage of evaluator creation."""
    print("=" * 80)
    print("KeywordsAI Create Evaluator Example")
    print("=" * 80)
    
    # Example 1: Simple LLM evaluator for response quality
    print("\n📊 Example 1: Creating LLM evaluator for response quality")
    print("-" * 80)
    
    evaluator_1 = create_llm_evaluator(
        name="Response Quality Evaluator",
        evaluator_slug="response_quality",
        evaluator_definition=(
            "Evaluate the quality of the assistant's response based on:\n"
            "1. Accuracy: Is the information correct?\n"
            "2. Relevance: Does it address the user's question?\n"
            "3. Completeness: Is the answer thorough?\n"
            "\n"
            "<llm_input>{{input}}</llm_input>\n"
            "<llm_output>{{output}}</llm_output>"
        ),
        scoring_rubric="0.0=Poor, 0.25=Below Average, 0.5=Average, 0.75=Good, 1.0=Excellent",
        description="Evaluates response quality on a 0-1 scale",
        min_score=DEFAULT_MIN_SCORE,
        max_score=DEFAULT_MAX_SCORE,
        passing_score=DEFAULT_PASSING_SCORE,
        model_options={
            "temperature": EVALUATOR_TEMPERATURE,
            "max_tokens": EVALUATOR_MAX_TOKENS
        }
    )
    
    # Example 2: Helpfulness evaluator with categorical scores
    print("\n📊 Example 2: Creating helpfulness evaluator (categorical)")
    print("-" * 80)
    
    evaluator_2 = create_evaluator(
        name="Helpfulness Evaluator",
        evaluator_slug="helpfulness_categorical",
        evaluator_type="llm",
        score_value_type="categorical",
        description="Evaluates if a response is helpful, neutral, or unhelpful",
        configurations={
            "evaluator_definition": (
                "Rate whether the assistant's response is helpful, neutral, or unhelpful.\n"
                "<llm_input>{{input}}</llm_input>\n"
                "<llm_output>{{output}}</llm_output>"
            ),
            "scoring_rubric": "helpful, neutral, unhelpful",
            "llm_engine": EVALUATOR_LLM_ENGINE,
            "model_options": {
                "temperature": EVALUATOR_TEMPERATURE,
                "max_tokens": 50
            }
        }
    )
    
    # Example 3: Factual accuracy evaluator (boolean)
    print("\n📊 Example 3: Creating factual accuracy evaluator (boolean)")
    print("-" * 80)
    
    evaluator_3 = create_evaluator(
        name="Factual Accuracy Evaluator",
        evaluator_slug="factual_accuracy",
        evaluator_type="llm",
        score_value_type="boolean",
        description="Checks if the response contains factual inaccuracies",
        configurations={
            "evaluator_definition": (
                "Determine if the assistant's response contains any factual inaccuracies.\n"
                "Respond with 'true' if the response is factually accurate, 'false' if it contains inaccuracies.\n"
                "\n"
                "<llm_input>{{input}}</llm_input>\n"
                "<llm_output>{{output}}</llm_output>"
            ),
            "scoring_rubric": "true=Factually accurate, false=Contains inaccuracies",
            "llm_engine": EVALUATOR_LLM_ENGINE,
            "model_options": {
                "temperature": 0.0,
                "max_tokens": 10
            }
        }
    )
    
    # Example 4: Custom numerical evaluator with 1-5 scale
    print("\n📊 Example 4: Creating custom numerical evaluator (1-5 scale)")
    print("-" * 80)
    
    evaluator_4 = create_llm_evaluator(
        name="Overall Satisfaction Evaluator",
        evaluator_slug="satisfaction_1_5",
        evaluator_definition=(
            "Rate the overall satisfaction with the assistant's response on a scale of 1-5:\n"
            "- Consider accuracy, helpfulness, clarity, and completeness\n"
            "\n"
            "<llm_input>{{input}}</llm_input>\n"
            "<llm_output>{{output}}</llm_output>"
        ),
        scoring_rubric="1=Very Dissatisfied, 2=Dissatisfied, 3=Neutral, 4=Satisfied, 5=Very Satisfied",
        description="Evaluates overall satisfaction on a 1-5 scale",
        min_score=1.0,
        max_score=5.0,
        passing_score=4.0,
        model_options={
            "temperature": EVALUATOR_TEMPERATURE,
            "max_tokens": 100
        }
    )
    
    print("\n" + "=" * 80)
    print("All evaluators created successfully!")
    print("=" * 80)
    
    return {
        "evaluator_1": evaluator_1,
        "evaluator_2": evaluator_2,
        "evaluator_3": evaluator_3,
        "evaluator_4": evaluator_4
    }


if __name__ == "__main__":
    main()
