import requests
import json
from ..constants import KEYWORDSAI_BASE_URL, KEYWORDSAI_BASE_HEADERS


def create_testset(name: str, description: str = "", column_definitions: list = None, starred: bool = False):
    """Create a new testset"""
    url = KEYWORDSAI_BASE_URL + "/testsets"
    headers = KEYWORDSAI_BASE_HEADERS
    
    if column_definitions is None:
        column_definitions = [
            {"field": "input"},
            {"field": "expected_output"}
        ]
    
    response = requests.post(
        url,
        headers=headers,
        json={
            "name": name,
            "description": description,
            "column_definitions": column_definitions,
            "starred": starred
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


def list_testsets(filters: dict = None):
    """List testsets with optional filters"""
    url = KEYWORDSAI_BASE_URL + "/testsets/list"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.post(
        url,
        headers=headers,
        json={"filters": filters} if filters else {}
    )
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def get_testset(testset_id: str):
    """Retrieve a specific testset"""
    url = KEYWORDSAI_BASE_URL + f"/testsets/{testset_id}"
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


def update_testset(testset_id: str, name: str = None, description: str = None, starred: bool = None):
    """Update testset metadata"""
    url = KEYWORDSAI_BASE_URL + f"/testsets/{testset_id}"
    headers = KEYWORDSAI_BASE_HEADERS
    
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if starred is not None:
        update_data["starred"] = starred
    
    response = requests.patch(url, headers=headers, json=update_data)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def create_testset_rows(testset_id: str, rows: list):
    """Create rows in a testset"""
    url = KEYWORDSAI_BASE_URL + f"/testsets/{testset_id}/rows"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.post(url, headers=headers, json=rows)
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def list_testset_rows(testset_id: str):
    """List rows in a testset"""
    url = KEYWORDSAI_BASE_URL + f"/testsets/{testset_id}/rows"
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


def update_testset_row(testset_id: str, row_index: int, row_data: dict):
    """Update a specific row in a testset"""
    url = KEYWORDSAI_BASE_URL + f"/testsets/{testset_id}/rows/{row_index}"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.patch(
        url,
        headers=headers,
        json={"row_data": row_data}
    )
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def delete_testset(testset_id: str):
    """Delete a testset"""
    url = KEYWORDSAI_BASE_URL + f"/testsets/{testset_id}"
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


def delete_testset_rows(testset_id: str, row_indexes: list):
    """Delete specific rows from a testset"""
    url = KEYWORDSAI_BASE_URL + f"/testsets/{testset_id}/rows"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.delete(
        url,
        headers=headers,
        json={"row_indexes": row_indexes}
    )
    try:
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return False


if __name__ == "__main__":
    # Test creating a testset
    testset = create_testset(
        name="Travel Agent Test Dataset",
        description="Dataset for testing travel agent tool calls",
        column_definitions=[
            {"field": "category"},
            {"field": "name"}, 
            {"field": "is_booking_hotel"},
            {"field": "is_checking_weather"},
            {"field": "expected_tools"}
        ]
    )
    
    if testset:
        print("Testset created:")
        print(json.dumps(testset, indent=2))
        
        # Add some sample rows
        sample_rows = [
            {
                "row_data": {
                    "category": "beach",
                    "name": "Mike (Beach Lover)",
                    "is_booking_hotel": False,
                    "is_checking_weather": False,
                    "expected_tools": "search_places"
                }
            },
            {
                "row_data": {
                    "category": "mountain", 
                    "name": "Sarah (Adventure Seeker)",
                    "is_booking_hotel": True,
                    "is_checking_weather": True,
                    "expected_tools": "search_places,find_hotels,check_weather"
                }
            }
        ]
        
        rows_result = create_testset_rows(testset["id"], sample_rows)
        if rows_result:
            print("Rows added successfully!")
