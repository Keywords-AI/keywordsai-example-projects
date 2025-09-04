import requests
import json
from ..constants import KEYWORDSAI_BASE_URL, KEYWORDSAI_BASE_HEADERS


def create_prompt(name: str, description: str = ""):
    """Create a new prompt"""
    url = KEYWORDSAI_BASE_URL + "/prompts/"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.post(
        url,
        headers=headers,
        json={
            "name": name,
            "description": description
        }
    )
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def list_prompts():
    """List all prompts"""
    url = KEYWORDSAI_BASE_URL + "/prompts/list"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.get(url, headers=headers)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def get_prompt(prompt_id: str):
    """Retrieve a specific prompt"""
    url = KEYWORDSAI_BASE_URL + f"/prompts/{prompt_id}/"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.get(url, headers=headers)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def update_prompt(prompt_id: str, name: str = None, description: str = None, deploy: bool = None):
    """Update a prompt"""
    url = KEYWORDSAI_BASE_URL + f"/prompts/{prompt_id}/"
    headers = KEYWORDSAI_BASE_HEADERS
    
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if deploy is not None:
        update_data["deploy"] = deploy
    
    response = requests.patch(url, headers=headers, json=update_data)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def delete_prompt(prompt_id: str):
    """Delete a prompt"""
    url = KEYWORDSAI_BASE_URL + f"/prompts/{prompt_id}"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.delete(url, headers=headers)
    try:
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return False


def create_prompt_version(prompt_id: str, messages: list, prompt_version_id: str = None):
    """Create a new version of a prompt"""
    url = KEYWORDSAI_BASE_URL + f"/prompts/{prompt_id}/versions"
    headers = KEYWORDSAI_BASE_HEADERS
    
    version_data = {
        "messages": messages
    }
    if prompt_version_id:
        version_data["prompt_version_id"] = prompt_version_id
    
    response = requests.post(url, headers=headers, json=version_data)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def list_prompt_versions(prompt_id: str):
    """List all versions of a prompt"""
    url = KEYWORDSAI_BASE_URL + f"/prompts/{prompt_id}/versions/"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.get(url, headers=headers)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def get_prompt_version(prompt_id: str, version_number: int):
    """Retrieve a specific version of a prompt"""
    url = KEYWORDSAI_BASE_URL + f"/prompts/{prompt_id}/versions/{version_number}/"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.get(url, headers=headers)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def update_prompt_version(prompt_id: str, version_number: int, deploy: bool = None, **kwargs):
    """Update a specific version of a prompt"""
    url = KEYWORDSAI_BASE_URL + f"/prompts/{prompt_id}/versions/{version_number}"
    headers = KEYWORDSAI_BASE_HEADERS
    
    update_data = {}
    if deploy is not None:
        update_data["deploy"] = deploy
    update_data.update(kwargs)
    
    response = requests.patch(url, headers=headers, json=update_data)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


if __name__ == "__main__":
    # Test creating a travel agent prompt
    prompt = create_prompt(
        name="Travel Agent Demo Prompt",
        description="Travel assistant with multi-modal inputs and tool calls"
    )
    
    if prompt:
        print("Prompt created:")
        print(json.dumps(prompt, indent=2))
        
        # Create a version with travel agent messages
        messages = [
            {
                "role": "system",
                "content": "You are a helpful travel assistant. Use the available tools to help users plan their trips based on their preferences."
            },
            {
                "role": "user", 
                "content": "User ({{name}}) chose category {{category}}{% if is_booking_hotel %}, wants to book hotel{% endif %}{% if is_checking_weather %}, wants to check weather{% endif %}"
            }
        ]
        
        version = create_prompt_version(prompt["prompt_id"], messages)
        if version:
            print("Prompt version created:")
            print(json.dumps(version, indent=2))
    else:
        print("Failed to create prompt")
