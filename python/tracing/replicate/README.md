# Replicate tracing examples

These examples trace the official `replicate` Python SDK with Respan. They load
environment variables from the repository root `.env` file.

Required for exporting traces:

```bash
RESPAN_API_KEY=...
```

For real Replicate calls, set:

```bash
REPLICATE_API_TOKEN=...
```

If `REPLICATE_API_TOKEN` is not set, the examples use the real Replicate SDK
against a deterministic in-process mock transport. That keeps the examples
runnable with the repo-root `.env` while still exercising the instrumentation
and exporting spans to Respan.

Optional environment variables:

```bash
RESPAN_BASE_URL=https://api.respan.ai/api
RESPAN_REPLICATE_MODEL=meta/meta-llama-3-8b-instruct
RESPAN_REPLICATE_MOCK=1
```

Run one script at a time:

```bash
python 01_run_prediction.py
python 02_stream_prediction.py
python 03_async_run_prediction.py
python 04_prediction_lifecycle.py
```

Or run the full set:

```bash
python run_all.py
```

Each script prints a `custom_identifier` and `workflow_name`. The workflow name
is also used as the Respan trace group identifier so the run is easy to find in
traces and MCP lookups.
