# Marqo Tracing Example

These examples use the current Marqo client to emit deterministic success and
service-error traces. The quickstart creates a temporary index, adds documents,
runs tensor search, and deletes the index. The failure probe records a bounded
Marqo 503 without making an external request.

## Run

Add `RESPAN_API_KEY` to the repository-root `.env`, then run:

```bash
cd python/tracing/marqo
pip install -r requirements.txt
RESPAN_EXAMPLE_RUN_ID=marqo-local python 01_quickstart.py
RESPAN_EXAMPLE_RUN_ID=marqo-local python 02_service_error.py
```

Without `MARQO_URL`, the examples start an ephemeral loopback protocol fixture;
the SDK itself is never replaced or mocked. To validate a real local service,
set `MARQO_URL`. For Marqo Cloud, set both `MARQO_URL` and `MARQO_API_KEY` in
the same `.env` file. The error probe always stays on loopback so it is safe to
run with production credentials. Both examples explicitly flush and shut down
Respan before exiting.
