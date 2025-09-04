import requests
import json
from .constants import KEYWORDSAI_BASE_URL, KEYWORDSAI_BASE_HEADERS


def test_evaluator(evaluator_slug: str, input_data: dict, output_data: dict):
    """Test an evaluator with sample data"""
    url = KEYWORDSAI_BASE_URL + f"/evaluators/{evaluator_slug}/run"
    headers = KEYWORDSAI_BASE_HEADERS
    
    payload = {
        "input": input_data,
        "output": output_data
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


if __name__ == "__main__":
    # Test the tool call accuracy evaluator with simple input/output format
    sample_input = "User (Mike Beach Lover) chose category beach, wants to book hotel: False, wants to check weather: False"
    
    sample_output = {
        "content": "Great choice, Mike! Beaches offer a perfect blend of relaxation and adventure. Could you please specify a location or destination you're interested in for your beach getaway?",
        "tool_calls": [
            {
                "id": "call_test123",
                "function": {
                    "name": "search_places",
                    "arguments": "{\"category\": \"beach\"}"
                },
                "type": "function"
            }
        ]
    }
    
    print("Testing tool call accuracy evaluator...")
    result = test_evaluator("tool_call_accuracy", sample_input, sample_output)
    
    if result:
        print("Evaluation result:")
        print(json.dumps(result, indent=2))
        print(f"\nScore: {result.get('score', 'N/A')}")
        print(f"Reasoning: {result.get('reasoning', 'N/A')}")
    else:
        print("Evaluation failed!")
