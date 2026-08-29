# Temporal tracing examples

These examples use Temporal's real local time-skipping test server with the
Respan interceptor. They cover workflow/activity success, a non-retried
activity failure, signal/query propagation, and history replay.

Install registry requirements, then link a local development package only for
validation:

```bash
pip install -r requirements.txt
pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-temporal
RESPAN_EXAMPLE_RUN_ID=temporal-check python run_all.py
```

The test server binary is downloaded by Temporal on first use. Every script
preserves an externally supplied marker and explicitly flushes and shuts down
Respan.
