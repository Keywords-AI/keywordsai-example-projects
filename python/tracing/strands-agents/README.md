# Strands Agents tracing examples

Runnable examples for `respan-instrumentation-strands-agents`.

## Setup

The scripts load credentials from the repository root `.env` file:

```text
respan-example-projects/.env
```

Required variable:

- `RESPAN_API_KEY`

Optional variables:

- `RESPAN_BASE_URL` defaults to `https://api.respan.ai/api`
- `RESPAN_STRANDS_MODEL` defaults to `gpt-4o-mini`

## Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
RESPAN_EXAMPLE_RUN_ID=strands-check python run_all.py
```

For local package development, link the instrumentation after installing the
portable registry requirements:

```bash
pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-strands-agents
```

`run_all.py` runs every script with one exact marker, continues after a failed
or timed-out child, and exits nonzero after reporting the aggregate failures.
Every script flushes and shuts down Respan in `finally`. The suite covers:

- `Strands Basic Example`
- `Strands Tool Use Example`
- `Strands Attribute Propagation Example`
- `Strands Structured Output Example`
- `Strands Expected Provider Error`
