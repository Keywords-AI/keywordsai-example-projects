import requests
import json
from ..constants import KEYWORDSAI_BASE_URL, KEYWORDSAI_BASE_HEADERS


def create_experiment(name: str, description: str = "", columns: list = None, rows: list = None):
    """Create a new experiment"""
    url = KEYWORDSAI_BASE_URL + "/experiments/create"
    headers = KEYWORDSAI_BASE_HEADERS
    
    experiment_data = {
        "name": name,
        "description": description
    }
    
    if columns:
        experiment_data["columns"] = columns
    if rows:
        experiment_data["rows"] = rows
    
    response = requests.post(url, headers=headers, json=experiment_data)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def list_experiments():
    """List all experiments"""
    url = KEYWORDSAI_BASE_URL + "/experiments/list"
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


def get_experiment(experiment_id: str):
    """Retrieve a specific experiment"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}"
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


def update_experiment(experiment_id: str, name: str = None, description: str = None):
    """Update experiment metadata"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}"
    headers = KEYWORDSAI_BASE_HEADERS
    
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    
    response = requests.patch(url, headers=headers, json=update_data)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def add_experiment_rows(experiment_id: str, rows: list):
    """Add rows to an experiment"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}/rows"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.post(url, headers=headers, json={"rows": rows})
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def remove_experiment_rows(experiment_id: str, row_ids: list):
    """Remove rows from an experiment"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}/rows"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.delete(url, headers=headers, json={"rows": row_ids})
    try:
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return False


def update_experiment_rows(experiment_id: str, rows: list):
    """Update rows in an experiment"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}/rows"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.patch(url, headers=headers, json={"rows": rows})
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def add_experiment_columns(experiment_id: str, columns: list):
    """Add columns to an experiment"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}/columns"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.post(url, headers=headers, json={"columns": columns})
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def remove_experiment_columns(experiment_id: str, column_ids: list):
    """Remove columns from an experiment"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}/columns"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.delete(url, headers=headers, json={"columns": column_ids})
    try:
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return False


def update_experiment_columns(experiment_id: str, columns: list):
    """Update columns in an experiment"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}/columns"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.patch(url, headers=headers, json={"columns": columns})
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def run_experiment(experiment_id: str, columns: list = None):
    """Run an experiment"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}/run"
    headers = KEYWORDSAI_BASE_HEADERS
    
    run_data = {}
    if columns:
        run_data["columns"] = columns
    
    response = requests.post(url, headers=headers, json=run_data)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def run_experiment_evals(experiment_id: str, evaluator_slugs: list):
    """Run evaluations on an experiment"""
    url = KEYWORDSAI_BASE_URL + f"/experiments/{experiment_id}/run-evals"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.post(
        url,
        headers=headers,
        json={"evaluator_slugs": evaluator_slugs}
    )
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


if __name__ == "__main__":
    # Test creating a simple experiment
    sample_columns = [
        {
            "model": "gpt-4o",
            "name": "Travel Agent v1",
            "temperature": 0.7,
            "max_completion_tokens": 256,
            "top_p": 1,
            "frequency_penalty": 0,
            "reasoning_effort": "low",
            "presence_penalty": 0,
            "prompt_messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "text": "You are a helpful travel assistant.",
                            "type": "text"
                        }
                    ]
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "text": "User {{name}} wants {{category}} travel.",
                            "type": "text"
                        }
                    ]
                }
            ],
            "tools": [],
            "tool_choice": "auto",
            "response_format": {"type": "text"}
        }
    ]
    
    sample_rows = [
        {
            "input": {
                "name": "Mike",
                "category": "beach"
            }
        }
    ]
    
    experiment = create_experiment(
        name="Travel Agent Experiment",
        description="Testing travel agent performance",
        columns=sample_columns,
        rows=sample_rows
    )
    
    if experiment:
        print("Experiment created:")
        print(json.dumps(experiment, indent=2))
