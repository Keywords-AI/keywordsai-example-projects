# OpenLIT Respan instrumentation examples

These examples exercise the local `respan-instrumentation-openlit` package with
current OpenLIT and OpenAI SDKs. They cover sync and async calls, Chat
Completions and Responses streaming, early stream close, real tool definitions
and execution, embeddings, a precise 429 error, and content-capture opt-out.

The default provider is a deterministic loopback server; it uses no model
credential and returns bounded fixtures. Set `RESPAN_OPENLIT_LIVE=1` to use the
`OPENAI_API_KEY` and optional `OPENAI_BASE_URL` from the repository `.env`
instead. Error and privacy examples always remain deterministic.

## Setup

From the workspace directory that contains both the `respan` and
`respan-example-projects` repositories:

```bash
python -m venv /private/tmp/respan-openlit-examples
/private/tmp/respan-openlit-examples/bin/pip install -r respan-example-projects/python/tracing/openlit/requirements.txt
/private/tmp/respan-openlit-examples/bin/pip install -e respan/python-sdks/respan-sdk -e respan/python-sdks/respan-tracing -e respan/python-sdks/respan -e respan/python-sdks/instrumentations/respan-instrumentation-openlit
```

`respan-example-projects/.env` must contain `RESPAN_API_KEY` (or
`RESPAN_GATEWAY_API_KEY`) for trace export. The examples verify that the
instrumentation distribution is actually linked to the local checkout.

## Run with an exact audit marker

Set the marker in the shell; the runner never invents or rewrites one:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-fix-py-group-21-openlit-dev-YYYYMMDDTHHMMSSZ \
  /private/tmp/respan-openlit-examples/bin/python \
  respan-example-projects/python/tracing/openlit/run_all_examples.py
```

Every process closes its OpenAI client, flushes and shuts down Respan, and the
runner enforces a 60-second timeout per example. Search the platform by the
exact `run_id` / `example_run_id`; scenario names identify each tree.
