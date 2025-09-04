import requests
import json
from ..constants import KEYWORDSAI_BASE_URL, KEYWORDSAI_BASE_HEADERS


def list_evaluators():
    url = KEYWORDSAI_BASE_URL + "/evaluators/list"
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


def create_llm_evaluator(
    evaluator_slug: str,
    name: str,
    evaluator_definition: str,
    scoring_rubric: str,
    description: str = "",
    min_score: float = 0.0,
    max_score: float = 1.0,
    passing_score: float = 0.8,
):
    url = KEYWORDSAI_BASE_URL + "/evaluators"
    headers = KEYWORDSAI_BASE_HEADERS
    response = requests.post(
        url,
        headers=headers,
        json={
            "evaluator_slug": evaluator_slug,
            "name": name,
            "description": description,
            "eval_class": "keywordsai_custom_llm",
            "configurations": {
                "evaluator_definition": evaluator_definition,
                "scoring_rubric": scoring_rubric,
                "min_score": min_score,
                "max_score": max_score,
                "passing_score": passing_score,
            },
        },
    )
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return response_data


def get_evaluator(evaluator_slug: str):
    url = KEYWORDSAI_BASE_URL + f"/evaluators/{evaluator_slug}"
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


if __name__ == "__main__":
    evaluators = list_evaluators()
    with open("evaluators.json", "w") as f:
        json.dump(evaluators, f, indent=4)
