# Apache Burr tracing examples

These deterministic examples cover successful and failed state-machine runs,
custom action spans with logged attributes, streaming lifecycle events, and
asynchronous execution.

Install this example set in a virtual environment linked to the local
`respan-instrumentation-burr` package, then run all scenarios with one marker:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-burr-check python run_all.py
```

Each script loads the repository-root `.env` and shuts down Respan explicitly.
