#!/usr/bin/env python3
"""
Create Dataset Example

This example demonstrates how to create and manage datasets in KeywordsAI.
Datasets are curated collections of logs (inputs/outputs + metadata) that you can
evaluate, annotate, and use to power Experiments.

Documentation: https://docs.keywordsai.co/documentation/products/dataset
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


def create_dataset(
    name: str,
    description: str = "",
    is_empty: bool = True,
    dataset_type: Optional[str] = None,
    sampling: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    initial_log_filters: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new dataset in Keywords AI.
    
    Args:
        name: Name of the dataset
        description: Optional description of the dataset
        is_empty: Whether to create an empty dataset (default: True)
        dataset_type: Type of dataset (e.g., "sampling")
        sampling: Sampling percentage or count
        start_time: Start time for sampling (ISO format)
        end_time: End time for sampling (ISO format)
        initial_log_filters: Filters for initial logs
        **kwargs: Additional fields
    
    Returns:
        Dict containing the created dataset data
    """
    url = f"{BASE_URL}/datasets/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "name": name,
        "description": description,
        "is_empty": is_empty
    }
    
    if dataset_type:
        payload["type"] = dataset_type
    if sampling is not None:
        payload["sampling"] = sampling
    if start_time:
        payload["start_time"] = start_time
    if end_time:
        payload["end_time"] = end_time
    if initial_log_filters:
        payload["initial_log_filters"] = initial_log_filters
    
    # Add any additional fields
    payload.update(kwargs)
    
    print("Creating dataset...")
    print(f"  URL: {url}")
    print(f"  Name: {name}")
    if description:
        print(f"  Description: {description}")
    print(f"  Is Empty: {is_empty}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Dataset created successfully")
    if 'id' in data:
        print(f"  Dataset ID: {data.get('id')}")
    if 'dataset_id' in data:
        print(f"  Dataset ID: {data.get('dataset_id')}")
    
    return data


def add_dataset_log(
    dataset_id: str,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Add a log entry to a dataset.
    
    Args:
        dataset_id: The ID of the dataset
        input_data: Input data (any JSON)
        output_data: Output data (any JSON)
        metadata: Optional metadata
        metrics: Optional metrics (cost, latency, etc.)
        **kwargs: Additional fields
    
    Returns:
        Dict containing the created log data
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/logs/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "input": input_data,
        "output": output_data
    }
    
    if metadata:
        payload["metadata"] = metadata
    if metrics:
        payload["metrics"] = metrics
    
    # Add any additional fields
    payload.update(kwargs)
    
    print("Adding dataset log...")
    print(f"  URL: {url}")
    print(f"  Dataset ID: {dataset_id}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Dataset log added successfully")
    if 'id' in data:
        print(f"  Log ID: {data.get('id')}")
    
    return data


def list_dataset_logs(
    dataset_id: str,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    List logs in a dataset.
    
    Args:
        dataset_id: The ID of the dataset
        page: Page number (default: 1)
        page_size: Number of items per page (default: 10)
    
    Returns:
        Dict containing the list of logs
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/logs/list/"
    params = {
        "page": page,
        "page_size": page_size
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print("Listing dataset logs...")
    print(f"  URL: {url}")
    print(f"  Dataset ID: {dataset_id}")
    print(f"  Page: {page}, Page Size: {page_size}")
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    logs = data if isinstance(data, list) else data.get('logs', data.get('results', []))
    
    print(f"\n✓ Found {len(logs)} log(s)")
    for i, log in enumerate(logs, 1):
        log_id = log.get('id', log.get('log_id', 'N/A'))
        print(f"  {i}. Log ID: {log_id}")
    
    return data


def bulk_add_logs(
    dataset_id: str,
    start_time: str,
    end_time: str,
    filters: Optional[Dict[str, Any]] = None,
    sampling_percentage: Optional[float] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Bulk add logs to a dataset using filters and time range.
    
    Args:
        dataset_id: The ID of the dataset
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        filters: Optional filters for logs
        sampling_percentage: Optional sampling percentage (0-100)
        **kwargs: Additional fields
    
    Returns:
        Dict containing the bulk operation result
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/logs/bulk/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "start_time": start_time,
        "end_time": end_time
    }
    
    if filters:
        payload["filters"] = filters
    if sampling_percentage is not None:
        payload["sampling_percentage"] = sampling_percentage
    
    # Add any additional fields
    payload.update(kwargs)
    
    print("Bulk adding logs to dataset...")
    print(f"  URL: {url}")
    print(f"  Dataset ID: {dataset_id}")
    print(f"  Time Range: {start_time} to {end_time}")
    if filters:
        print(f"  Filters: {json.dumps(filters, indent=2)}")
    if sampling_percentage:
        print(f"  Sampling: {sampling_percentage}%")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Bulk add operation initiated")
    print(f"  Note: This runs in the background. Use list_dataset_logs() to check when logs appear.")
    
    return data


def run_eval_on_dataset(
    dataset_id: str,
    evaluator_slugs: List[str]
) -> Dict[str, Any]:
    """
    Run evaluators on all logs in a dataset.
    
    Args:
        dataset_id: The ID of the dataset
        evaluator_slugs: List of evaluator slugs to run
    
    Returns:
        Dict containing the eval run result
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/eval-reports/create"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "evaluator_slugs": evaluator_slugs
    }
    
    print("Running eval on dataset...")
    print(f"  URL: {url}")
    print(f"  Dataset ID: {dataset_id}")
    print(f"  Evaluator Slugs: {evaluator_slugs}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Eval run initiated")
    if 'id' in data:
        print(f"  Eval Report ID: {data.get('id')}")
    if 'report_id' in data:
        print(f"  Report ID: {data.get('report_id')}")
    
    return data


def list_eval_runs(
    dataset_id: str
) -> List[Dict[str, Any]]:
    """
    List all eval runs for a dataset.
    
    Args:
        dataset_id: The ID of the dataset
    
    Returns:
        List of eval run dictionaries
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/eval-reports/list/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print("Listing eval runs...")
    print(f"  URL: {url}")
    print(f"  Dataset ID: {dataset_id}")
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    runs = data if isinstance(data, list) else data.get('runs', data.get('results', []))
    
    print(f"\n✓ Found {len(runs)} eval run(s)")
    for i, run in enumerate(runs, 1):
        run_id = run.get('id', run.get('report_id', 'N/A'))
        status = run.get('status', 'N/A')
        print(f"  {i}. Run ID: {run_id}, Status: {status}")
    
    return runs


def update_dataset(
    dataset_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update dataset metadata.
    
    Args:
        dataset_id: The ID of the dataset
        name: Optional new name
        description: Optional new description
        **kwargs: Additional fields to update
    
    Returns:
        Dict containing the updated dataset data
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    
    # Add any additional fields
    payload.update(kwargs)
    
    print("Updating dataset...")
    print(f"  URL: {url}")
    print(f"  Dataset ID: {dataset_id}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(f"\n✓ Dataset updated successfully")
    
    return data


def delete_dataset_logs(
    dataset_id: str,
    filters: Optional[Dict[str, Any]] = None,
    delete_all: bool = False
) -> Dict[str, Any]:
    """
    Delete logs from a dataset.
    
    Args:
        dataset_id: The ID of the dataset
        filters: Optional filters to match logs to delete
        delete_all: If True, delete all logs (use with caution)
    
    Returns:
        Dict containing the deletion result
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/logs/delete/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {}
    if delete_all:
        payload["delete_all"] = True
    elif filters:
        payload["filters"] = filters
    else:
        raise ValueError("Either filters or delete_all must be provided")
    
    print("Deleting dataset logs...")
    print(f"  URL: {url}")
    print(f"  Dataset ID: {dataset_id}")
    if delete_all:
        print(f"  ⚠️  WARNING: Deleting ALL logs!")
    else:
        print(f"  Filters: {json.dumps(filters, indent=2)}")
    print(f"  Request Body: {json.dumps(payload, indent=2)}")
    
    response = requests.delete(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json() if response.text else {}
    print(f"\n✓ Logs deleted successfully")
    
    return data


def delete_dataset(dataset_id: str) -> bool:
    """
    Delete a dataset.
    
    Args:
        dataset_id: The ID of the dataset to delete
    
    Returns:
        True if successful
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print("Deleting dataset...")
    print(f"  URL: {url}")
    print(f"  Dataset ID: {dataset_id}")
    print(f"  ⚠️  WARNING: This will permanently delete the dataset!")
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        print(f"\n✓ Dataset deleted successfully")
        return True
    else:
        response.raise_for_status()
        return False


def main():
    """Example usage of dataset creation and management."""
    print("=" * 80)
    print("KeywordsAI Create Dataset Example")
    print("=" * 80)
    
    # Example 1: Create an empty dataset
    print("\n📝 Example 1: Creating an empty dataset")
    print("-" * 80)
    
    dataset_1 = create_dataset(
        name="Demo Dataset (via API)",
        description="Created from docs tutorial",
        is_empty=True
    )
    dataset_1_id = dataset_1.get('id') or dataset_1.get('dataset_id')
    
    # Example 2: Add a dataset log
    print("\n📝 Example 2: Adding a dataset log")
    print("-" * 80)
    
    if dataset_1_id:
        log_1 = add_dataset_log(
            dataset_id=dataset_1_id,
            input_data={
                "question": "What is 2+2?",
                "context": {"source": "docs_tutorial"}
            },
            output_data={
                "answer": "4",
                "explanation": "2 + 2 = 4."
            },
            metadata={
                "custom_identifier": "dataset-tutorial-log-1",
                "model": "gpt-4o-mini"
            },
            metrics={
                "cost": 0.0,
                "latency": 0.0
            }
        )
        
        # Add another log
        log_2 = add_dataset_log(
            dataset_id=dataset_1_id,
            input_data={
                "question": "What is the capital of France?",
                "context": {"source": "docs_tutorial"}
            },
            output_data={
                "answer": "Paris",
                "explanation": "Paris is the capital and largest city of France."
            },
            metadata={
                "custom_identifier": "dataset-tutorial-log-2",
                "model": "gpt-4o-mini"
            },
            metrics={
                "cost": 0.0,
                "latency": 0.0
            }
        )
    
    # Example 3: List dataset logs
    print("\n📝 Example 3: Listing dataset logs")
    print("-" * 80)
    
    if dataset_1_id:
        logs = list_dataset_logs(dataset_1_id, page=1, page_size=10)
    
    # Example 4: Update dataset metadata
    print("\n📝 Example 4: Updating dataset metadata")
    print("-" * 80)
    
    if dataset_1_id:
        updated_dataset = update_dataset(
            dataset_id=dataset_1_id,
            name="Updated Demo Dataset",
            description="Updated via API"
        )
    
    # Example 5: Create another dataset for eval demonstration
    print("\n📝 Example 5: Creating another dataset for eval")
    print("-" * 80)
    
    dataset_2 = create_dataset(
        name="Eval Test Dataset",
        description="Dataset for testing evaluators",
        is_empty=True
    )
    dataset_2_id = dataset_2.get('id') or dataset_2.get('dataset_id')
    
    if dataset_2_id:
        # Add a log to the second dataset
        add_dataset_log(
            dataset_id=dataset_2_id,
            input_data={
                "question": "What is machine learning?",
                "context": {"source": "eval_test"}
            },
            output_data={
                "answer": "Machine learning is a subset of AI that enables systems to learn from data.",
                "explanation": "It uses algorithms to identify patterns and make decisions."
            },
            metadata={
                "custom_identifier": "eval-test-log-1",
                "model": "gpt-4o"
            },
            metrics={
                "cost": 0.001,
                "latency": 0.5
            }
        )
        
        # Example 6: Run eval on dataset (if evaluators exist)
        print("\n📝 Example 6: Running eval on dataset")
        print("-" * 80)
        print("Note: This requires existing evaluators. If you don't have evaluators,")
        print("      create them first using create_evaluator.py")
        print("-" * 80)
        
        # Uncomment and replace with actual evaluator slugs if you have them
        # eval_result = run_eval_on_dataset(
        #     dataset_id=dataset_2_id,
        #     evaluator_slugs=["response_quality"]  # Replace with your evaluator slug
        # )
        
        # Example 7: List eval runs
        print("\n📝 Example 7: Listing eval runs")
        print("-" * 80)
        
        eval_runs = list_eval_runs(dataset_2_id)
    
    # Example 8: Delete logs from dataset (by filter)
    print("\n📝 Example 8: Deleting logs from dataset (by filter)")
    print("-" * 80)
    print("Note: Skipping actual deletion to preserve test data.")
    print("      Uncomment the code below to test deletion.")
    print("-" * 80)
    
    # Uncomment to test deletion
    # if dataset_1_id:
    #     delete_dataset_logs(
    #         dataset_id=dataset_1_id,
    #         filters={"metadata.custom_identifier": "dataset-tutorial-log-1"}
    #     )
    
    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
    print("\n💡 Tips:")
    print("   - You can view your datasets on the KeywordsAI platform")
    print("   - Use datasets to power Experiments and compare prompt versions")
    print("   - Run evaluators on datasets to assess quality at scale")
    print(f"\n📊 Created Dataset IDs:")
    if dataset_1_id:
        print(f"   - Dataset 1: {dataset_1_id}")
    if dataset_2_id:
        print(f"   - Dataset 2: {dataset_2_id}")
    
    return {
        "dataset_1": dataset_1,
        "dataset_2": dataset_2
    }


if __name__ == "__main__":
    main()
