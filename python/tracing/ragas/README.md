# Ragas tracing examples

These examples validate current Ragas 0.4 evaluation, collection metrics, and
experiment APIs with Respan OTel 2.x instrumentation. They are deterministic
and need only the repository `RESPAN_API_KEY`.

For local instrumentation development, install the Ragas package from the
adjacent `respan` checkout in editable mode, then run:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-ragas-check python run_all.py
```

The runner preserves an existing marker, runs every process with a timeout,
continues after failures, and returns nonzero when any example fails.
