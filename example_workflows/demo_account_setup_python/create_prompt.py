#!/usr/bin/env python3
"""
Create Prompt Example

This example demonstrates how to create and manage prompts in KeywordsAI.
Prompts are reusable templates for LLM conversations that can be versioned and deployed.

Documentation: https://docs.keywordsai.co/get-started/quickstart/create-a-prompt
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

# Prompt configuration from environment variables
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")
DEFAULT_TEMPERATURE = float(os.getenv("PROMPT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("PROMPT_MAX_TOKENS", "256"))


def create_prompt(
    name: str,
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a new prompt in Keywords AI.
    
    Args:
        name: Name of the prompt
        description: Optional description of the prompt
    
    Returns:
        Dict containing the created prompt data
    """
    url = f"{BASE_URL}/prompts/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "name": name,
        "description": description
    }
    
    print("Creating prompt...")
    print(f"  URL: {url}")
    print(f"  Name: {name}")
    if description:
        print(f"  Description: {description}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Prompt created successfully")
    if 'prompt_id' in data:
        print(f"  Prompt ID: {data.get('prompt_id')}")
    if 'id' in data:
        print(f"  Prompt ID: {data.get('id')}")
    
    return data


def create_prompt_version(
    prompt_id: str,
    messages: List[Dict[str, str]],
    description: str = "",
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    variables: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new version of a prompt.
    
    Args:
        prompt_id: The ID of the prompt to create a version for
        messages: List of messages in OpenAI format (role and content)
        description: Optional description of this version
        model: Optional model name (e.g., "gpt-4o", "gpt-3.5-turbo")
        temperature: Optional temperature setting
        max_tokens: Optional maximum tokens
        stream: Whether to stream responses
        variables: Optional variables for template substitution
        **kwargs: Additional configuration options
    
    Returns:
        Dict containing the created prompt version data
    """
    url = f"{BASE_URL}/prompts/{prompt_id}/versions/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "messages": messages
    }
    
    if description:
        payload["description"] = description
    if model:
        payload["model"] = model
    if temperature is not None:
        payload["temperature"] = temperature
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if stream:
        payload["stream"] = stream
    if variables:
        payload["variables"] = variables
    
    # Add any additional fields
    payload.update(kwargs)
    
    print("Creating prompt version...")
    print(f"  URL: {url}")
    print(f"  Prompt ID: {prompt_id}")
    print(f"  Messages: {len(messages)}")
    if model:
        print(f"  Model: {model}")
    if description:
        print(f"  Description: {description}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Prompt version created successfully")
    if 'version_number' in data:
        print(f"  Version Number: {data.get('version_number')}")
    if 'prompt_version_id' in data:
        print(f"  Prompt Version ID: {data.get('prompt_version_id')}")
    
    return data


def list_prompts() -> List[Dict[str, Any]]:
    """
    List all prompts in the account.
    
    Returns:
        List of prompt dictionaries
    """
    url = f"{BASE_URL}/prompts/list"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print("Listing prompts...")
    print(f"  URL: {url}")
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    prompts = data if isinstance(data, list) else data.get('prompts', [])
    
    print(f"\n✓ Found {len(prompts)} prompt(s)")
    for i, prompt in enumerate(prompts, 1):
        print(f"  {i}. {prompt.get('name', 'Unnamed')} (ID: {prompt.get('prompt_id', prompt.get('id', 'N/A'))})")
    
    return prompts


def get_prompt(prompt_id: str) -> Dict[str, Any]:
    """
    Get a specific prompt by ID.
    
    Args:
        prompt_id: The ID of the prompt to retrieve
    
    Returns:
        Dict containing the prompt data
    """
    url = f"{BASE_URL}/prompts/{prompt_id}/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print("Getting prompt...")
    print(f"  URL: {url}")
    print(f"  Prompt ID: {prompt_id}")
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Prompt retrieved successfully")
    print(f"  Name: {data.get('name', 'N/A')}")
    print(f"  Description: {data.get('description', 'N/A')}")
    
    return data


def list_prompt_versions(prompt_id: str) -> List[Dict[str, Any]]:
    """
    List all versions of a prompt.
    
    Args:
        prompt_id: The ID of the prompt
    
    Returns:
        List of prompt version dictionaries
    """
    url = f"{BASE_URL}/prompts/{prompt_id}/versions/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print("Listing prompt versions...")
    print(f"  URL: {url}")
    print(f"  Prompt ID: {prompt_id}")
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    versions = data if isinstance(data, list) else data.get('versions', [])
    
    print(f"\n✓ Found {len(versions)} version(s)")
    for i, version in enumerate(versions, 1):
        version_num = version.get('version_number', version.get('version', 'N/A'))
        print(f"  {i}. Version {version_num}")
    
    return versions


def get_prompt_version(prompt_id: str, version_number: int) -> Dict[str, Any]:
    """
    Get a specific version of a prompt.
    
    Args:
        prompt_id: The ID of the prompt
        version_number: The version number to retrieve
    
    Returns:
        Dict containing the prompt version data
    """
    url = f"{BASE_URL}/prompts/{prompt_id}/versions/{version_number}/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print("Getting prompt version...")
    print(f"  URL: {url}")
    print(f"  Prompt ID: {prompt_id}")
    print(f"  Version Number: {version_number}")
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Prompt version retrieved successfully")
    if 'messages' in data:
        print(f"  Messages: {len(data.get('messages', []))}")
    
    return data


def main():
    """Example usage of prompt creation and management."""
    print("=" * 80)
    print("KeywordsAI Create Prompt Example")
    print("=" * 80)
    
    # Example 1: Create a simple prompt
    print("\n📝 Example 1: Creating a simple prompt")
    print("-" * 80)
    
    prompt_1 = create_prompt(
        name="Customer Support Assistant",
        description="A helpful assistant for customer support queries"
    )
    prompt_1_id = prompt_1.get('prompt_id') or prompt_1.get('id')
    
    # Example 2: Create a prompt version with messages
    print("\n📝 Example 2: Creating a prompt version with messages")
    print("-" * 80)
    
    if prompt_1_id:
        version_1 = create_prompt_version(
            prompt_id=prompt_1_id,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful customer support assistant. Be polite, professional, and solution-oriented."
                },
                {
                    "role": "user",
                    "content": "{{user_query}}"
                }
            ],
            description="Initial version with basic customer support setup",
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            variables={
                "user_query": "How can I help you today?"
            }
        )
    
    # Example 3: Create a more complex prompt with multiple messages
    print("\n📝 Example 3: Creating a complex prompt with multiple messages")
    print("-" * 80)
    
    prompt_2 = create_prompt(
        name="Travel Planning Assistant",
        description="An AI assistant that helps users plan their travel itineraries"
    )
    prompt_2_id = prompt_2.get('prompt_id') or prompt_2.get('id')
    
    if prompt_2_id:
        version_2 = create_prompt_version(
            prompt_id=prompt_2_id,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert travel planner. Help users create detailed travel itineraries based on their preferences, budget, and destination."
                },
                {
                    "role": "user",
                    "content": "I want to plan a trip to {{destination}} for {{duration}} days. My budget is {{budget}} and I'm interested in {{interests}}."
                }
            ],
            description="Travel planning prompt with template variables",
            model=DEFAULT_MODEL,
            temperature=0.8,
            max_tokens=512,
            variables={
                "destination": "Paris",
                "duration": "5",
                "budget": "$2000",
                "interests": "museums, food, architecture"
            }
        )
    
    # Example 4: List all prompts
    print("\n📝 Example 4: Listing all prompts")
    print("-" * 80)
    
    all_prompts = list_prompts()
    
    # Example 5: Get a specific prompt
    print("\n📝 Example 5: Getting a specific prompt")
    print("-" * 80)
    
    if prompt_1_id:
        retrieved_prompt = get_prompt(prompt_1_id)
    
    # Example 6: List prompt versions
    print("\n📝 Example 6: Listing prompt versions")
    print("-" * 80)
    
    if prompt_1_id:
        versions = list_prompt_versions(prompt_1_id)
        
        # Example 7: Get a specific prompt version
        if versions:
            print("\n📝 Example 7: Getting a specific prompt version")
            print("-" * 80)
            version_num = versions[0].get('version_number', versions[0].get('version', 1))
            if isinstance(version_num, int):
                version_data = get_prompt_version(prompt_1_id, version_num)
    
    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
    print("\n💡 Tip: You can now use these prompts in your experiments and evaluations.")
    print("   Visit the KeywordsAI platform to see your prompts in the Prompt Management section.")
    
    return {
        "prompt_1": prompt_1,
        "prompt_2": prompt_2,
        "all_prompts": all_prompts
    }


if __name__ == "__main__":
    main()
