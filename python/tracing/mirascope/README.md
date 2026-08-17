# Mirascope tracing examples

These examples exercise Mirascope 2.x model calls, sync and async streams,
tool-call execution, privacy mode, deterministic provider errors, and an
OpenAI-compatible live call through the Respan gateway.

The scripts load `RESPAN_API_KEY`, `RESPAN_BASE_URL`, and optional gateway
overrides from the repository-root `.env`. Every script adds the exact
`RESPAN_EXAMPLE_RUN_ID` to its trace metadata and explicitly flushes and shuts
down Respan.

Install the dependencies:

```bash
cd python/tracing/mirascope
pip install -r requirements.txt
```

When validating an unpublished branch, link the local packages:

```bash
pip install -e ../../../../respan/python-sdks/respan-sdk
pip install -e ../../../../respan/python-sdks/respan-tracing
pip install -e ../../../../respan/python-sdks/respan
pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-mirascope
```

Run the complete set with one marker:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-fix-py-group-19-YYYYMMDDTHHMMSSZ python run_all.py
```

`05_live_gateway.py` runs by default with the repository credentials. Set
`RESPAN_MIRASCOPE_RUN_LIVE=0` to skip only that optional provider-backed call.

| Script | Coverage |
| --- | --- |
| `01_call_and_tool.py` | Real `Model.call`, `ToolCall`, and `Toolkit.execute` objects |
| `02_sync_async_stream.py` | Consumed real sync and async stream objects plus usage |
| `03_expected_error.py` | Exact provider 503 escaping the workflow boundary |
| `04_privacy.py` | Content capture disabled while model, usage, and status remain |
| `05_live_gateway.py` | Mirascope OpenAI provider through the Respan gateway |
