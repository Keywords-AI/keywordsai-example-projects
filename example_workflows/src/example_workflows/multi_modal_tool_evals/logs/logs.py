import json
import requests
from ..constants import KEYWORDSAI_BASE_URL, KEYWORDSAI_BASE_HEADERS
from datetime import datetime
from urllib.parse import urlencode


def get_logs(start_time: datetime, end_time: datetime, filters: dict = None):
    url = KEYWORDSAI_BASE_URL + "/request-logs/list"
    headers = KEYWORDSAI_BASE_HEADERS
    url_params = {
        "start_time": start_time,
        "end_time": end_time,
    }
    url_params = urlencode(url_params)
    response = requests.post(
        url=url + "?" + url_params,
        headers=headers,
        json={"filters": filters},
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
    logs = get_logs()
    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4)
