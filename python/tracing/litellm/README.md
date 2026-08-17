# LiteLLM Respan Instrumentation Examples

These examples demonstrate `respan-instrumentation-litellm` with LiteLLM
completions routed through the Respan OpenAI-compatible gateway. Each script
loads `.env` from the repository root and stamps a readable workflow name on
the trace.

## Setup

From the repository root:

```bash
pip install -r python/tracing/litellm/requirements.txt
```

The scripts use the root `.env` file. Required values:

- `RESPAN_API_KEY` for trace export
- `RESPAN_GATEWAY_API_KEY` or `RESPAN_API_KEY` for LiteLLM gateway calls
- `RESPAN_GATEWAY_BASE_URL` or `RESPAN_BASE_URL` for the gateway base URL
- `RESPAN_MODEL` or `RESPAN_LITELLM_MODEL` for the model

## Run

```bash
python python/tracing/litellm/01_basic_completion.py
python python/tracing/litellm/02_streaming_completion.py
python python/tracing/litellm/03_respan_attributes.py
python python/tracing/litellm/04_tool_calling.py
python python/tracing/litellm/05_expected_error.py
python python/tracing/litellm/06_async_completion.py
python python/tracing/litellm/07_async_streaming.py
```

Or run all examples:

```bash
python python/tracing/litellm/run_all_examples.py
```

## Workflow Names

The examples are searchable in Respan by these workflow names:

- `litellm_basic_completion.workflow`
- `litellm_streaming_completion.workflow`
- `litellm_respan_attributes.workflow`
- `litellm_tool_calling.workflow`
- `litellm_expected_error.workflow`
- `litellm_async_completion.workflow`
- `litellm_async_streaming.workflow`

Every script shuts down Respan in `finally`. The set covers sync/async,
stream/non-stream, canonical tool schemas/calls, propagated attributes, and a
controlled expected provider error.
