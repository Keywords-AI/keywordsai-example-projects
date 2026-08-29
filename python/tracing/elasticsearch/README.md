# Elasticsearch tracing examples

These examples use the real synchronous and asynchronous Elasticsearch Python
clients against a deterministic local HTTP server, so no Elasticsearch cluster
or credentials are required. Traces are exported with the `RESPAN_API_KEY` from
the repository root `.env` file.

Run both examples with one marker:

```bash
RESPAN_EXAMPLE_RUN_ID=my-audit-marker python run_all.py
```
