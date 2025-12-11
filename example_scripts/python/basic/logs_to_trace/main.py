#!/usr/bin/env python3
"""
Trace Log Demo

This script demonstrates how to send trace logs to KeywordsAI while avoiding ID collisions.

Files:
- trace_logs.json: Sample trace data - clean, accurate payload format exactly as it would appear in the payload
- utils.py: Processing utilities that shift timestamps and remap IDs
- main.py: This demo script (2 lines of logic)

How it works:
1. generate_trace_data() takes the sample logs and shifts timestamps to current time
2. It remaps trace_unique_id and span_unique_id to prevent aggregation onto wrong traces  
3. Data shape remains unchanged - only timestamps and IDs are modified
4. Processed logs are sent directly to KeywordsAI traces endpoint

Usage:
    cd keywordsai/logs_to_trace/
    python3 main.py
"""

import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from utils import generate_trace_data
from pathlib import Path

load_dotenv(override=True)
parent_dir = Path(__file__).parent.resolve()
file_name = parent_dir / "trace_logs.json"

processed_logs = generate_trace_data(
    json.load(open(file_name)), datetime.now(timezone.utc)
)
response = requests.post(
    f"{os.getenv('KEYWORDSAI_BASE_URL')}/v1/traces/ingest",
    json=processed_logs,
    headers={"Authorization": f"Bearer {os.getenv('KEYWORDSAI_API_KEY')}"},
)

print(
    f"Status: {response.status_code}, Trace ID: {processed_logs[0]['trace_unique_id']}"
)
