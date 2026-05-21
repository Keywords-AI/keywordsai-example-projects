# Braintrust Tracing Examples

These examples show Braintrust spans exported to Respan through
`respan-instrumentation-braintrust`.

Each script loads the repo-root `.env`, creates a root Braintrust span named
`<workflow name>.workflow`, and propagates the same workflow name to
`trace_group_identifier` so traces are easy to recognize in Respan.

## Install

```bash
cd python/tracing/braintrust
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

## Run

```bash
.venv/bin/python 01_basic_workflow.py
.venv/bin/python 02_nested_tool_workflow.py
.venv/bin/python 03_scored_evaluation_workflow.py
```

Each script prints:

- `workflow_name`: the visible workflow name to search in Respan
- `RESPAN_EXAMPLE_RUN_ID`: the exact run id also stored in trace metadata

