# Logs to Trace Example

This example demonstrates how to send trace logs to KeywordsAI while avoiding ID collisions by processing existing trace data.

## How it works

1. Loads sample trace data from `trace_logs.json`
2. Shifts timestamps to current time while preserving relative timing
3. Remaps trace and span IDs to prevent conflicts with existing traces
4. Sends processed logs to KeywordsAI traces endpoint

## Setup

```bash
pip install -r requirements.txt
```

Set environment variables:
- `KEYWORDSAI_API_KEY`: Your KeywordsAI API key
- `KEYWORDSAI_BASE_URL`: KeywordsAI base URL

## Usage

```bash
python main.py
```
