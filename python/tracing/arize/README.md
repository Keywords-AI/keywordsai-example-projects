# Arize Python SDK tracing examples

These examples demonstrate `respan-instrumentation-arize` against the public
`arize` Python SDK client surface. The examples install deterministic offline
responses beneath the SDK's public methods before Respan activates the
instrumentor, so they create Respan traces without requiring an Arize account.

Run from this directory after installing the local packages:

```bash
python run_all.py
```

The examples load Respan credentials from the repository root `.env` file and
print `workflow_name` plus `RESPAN_EXAMPLE_RUN_ID` for MCP lookup.
