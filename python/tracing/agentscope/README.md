# AgentScope Respan Tracing Examples

These examples demonstrate AgentScope tracing with
`respan-instrumentation-agentscope`. They use deterministic local AgentScope
models and tools so the traces are repeatable and do not require provider API
keys.

## Setup

The scripts load credentials from the repository root `.env`:

- `RESPAN_API_KEY` for trace export
- `RESPAN_BASE_URL` optional, defaulting to `https://api.respan.ai/api`
- `RESPAN_EXAMPLE_RUN_ID` optional, used to group example runs

Install dependencies:

```bash
cd python/tracing/agentscope
pip install -r requirements.txt
```

For local instrumentation development:

```bash
pip install -e ../../../../respan/python-sdks/respan-sdk \
            -e ../../../../respan/python-sdks/respan-tracing \
            -e ../../../../respan/python-sdks/respan \
            -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-agentscope \
            -r requirements.txt
```

## Examples

| Script | Coverage |
| --- | --- |
| `01_agent_and_model.py` | Direct chat model call plus `Agent.reply()` |
| `02_tool_call.py` | Agent tool/function call through `Toolkit.call_tool()` |
| `03_multi_agent_and_failure.py` | Multi-agent `observe()` flow plus deterministic failure span |

Run an example:

```bash
python 01_agent_and_model.py
```
