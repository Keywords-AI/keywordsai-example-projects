# smolagents Respan Examples

These examples show smolagents traces exported through `respan-instrumentation-smolagents`.

## Setup

The scripts load credentials from the repo root `.env`:

- `RESPAN_API_KEY` for trace export
- `RESPAN_GATEWAY_API_KEY` or `RESPAN_API_KEY` for model calls
- `RESPAN_GATEWAY_BASE_URL` or `RESPAN_BASE_URL` for the OpenAI-compatible gateway
- `RESPAN_MODEL` for the model name, defaulting to `gpt-4o-mini`

Install from local source while developing:

```bash
uv venv /tmp/respan-smolagents-example-venv
/tmp/respan-smolagents-example-venv/bin/python -m pip install \
  -e ../../../../respan/python-sdks/respan-sdk \
  -e ../../../../respan/python-sdks/respan-tracing \
  -e ../../../../respan/python-sdks/respan \
  -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-openinference \
  -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-smolagents \
  -r requirements.txt
```

Run the examples:

```bash
python run_all.py
```

## Examples

| Script | Coverage |
|--------|----------|
| `01_code_agent.py` | `CodeAgent` planning, code execution, local tool use, and LLM spans under `smolagents_code_agent_workflow` |
| `02_tool_calling_agent.py` | `ToolCallingAgent` function-tool planning and LLM spans under `smolagents_tool_calling_agent_workflow` |
| `03_expected_tool_failure.py` | Deterministic connected tool failure with the exception escaping the workflow wrapper |
| `04_streaming_agent.py` | Streamed `ToolCallingAgent` execution with bounded semantic workflow input/output |

`run_all.py` preserves one externally supplied `RESPAN_EXAMPLE_RUN_ID`, applies
a timeout to every child process, runs every scenario even after a failure, and
returns a non-zero exit when any scenario fails.
