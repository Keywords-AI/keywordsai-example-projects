# Replicate tracing examples

These examples trace the official `replicate` Python SDK with Respan. They load
environment variables from the repository root `.env` file.

Required for exporting traces:

```bash
RESPAN_API_KEY=...
```

The committed validation path always uses the real Replicate SDK against a
deterministic `httpx.MockTransport`. To opt into billable provider calls, set:

```bash
REPLICATE_API_TOKEN=...
RESPAN_REPLICATE_LIVE=1
```

Optional environment variables:

```bash
RESPAN_BASE_URL=https://api.respan.ai/api
RESPAN_REPLICATE_MODEL=meta/meta-llama-3-8b-instruct
RESPAN_EXAMPLE_RUN_ID=otel2-replicate-check
```

Run one script at a time:

```bash
python 01_run_prediction.py
python 02_stream_prediction.py
python 03_async_run_prediction.py
python 04_prediction_lifecycle.py
python 05_expected_error.py
```

Or run the full set:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-replicate-check python run_all.py
```

Each script prints a `custom_identifier` and `workflow_name`. The workflow name
is also used as the Respan trace group identifier so the run is easy to find in
traces and MCP lookups.
