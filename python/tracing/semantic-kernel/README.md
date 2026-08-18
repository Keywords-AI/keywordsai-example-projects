# Semantic Kernel tracing examples

These examples run Microsoft Semantic Kernel through Respan tracing and the
Respan gateway. They cover direct kernel function invocation, chat completion,
automatic plugin/tool invocation, and a deterministic failing function.

The scripts load environment variables from the examples repo root `.env` file:

- `RESPAN_API_KEY`
- `RESPAN_BASE_URL`
- `RESPAN_GATEWAY_API_KEY`
- `RESPAN_GATEWAY_BASE_URL`
- `RESPAN_MODEL`

Run the complete set from this directory after installing local packages:

```bash
python run_all.py
```

The runner preserves an externally supplied `RESPAN_EXAMPLE_RUN_ID`, applies a
timeout to every process, continues after individual failures, and reports the
aggregate result. The failure scenario lets the exception escape the decorated
workflow before catching it in `main`, so both native tool and workflow status
are observable.
