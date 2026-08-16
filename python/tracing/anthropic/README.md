# Python Anthropic tracing

This directory validates the locally linked `respan-instrumentation-anthropic`
package against the Respan Anthropic gateway. It covers a basic Messages call,
stream aggregation, a forced tool round, and an expected provider 404.

From `respan-example-projects`, run:

```bash
python -m pip install -r python/tracing/anthropic/requirements.txt
RESPAN_EXAMPLE_RUN_ID=my-marker python python/tracing/anthropic/run_all.py
```

The examples load credentials from the repository root `.env`, prefer the
sibling local `respan` checkout, propagate the exact marker to every scenario,
and always shut down tracing before exiting.
