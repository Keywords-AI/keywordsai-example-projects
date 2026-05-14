# AutoGen Respan Integration Examples

These examples demonstrate how to trace AutoGen AgentChat applications with
Respan using `respan-instrumentation-autogen`.

Each script wraps the run in a Respan workflow whose name matches the script
filename, so the platform result is easy to map back to the example.

All scripts load environment variables from the repository root:

```text
respan-example-projects/.env
```

## Setup

```bash
cd python/tracing/autogen
pip install -r requirements.txt
```

For local development against the sibling `respan` checkout:

```bash
pip install -e ../../../../respan/python-sdks/respan-sdk \
            -e ../../../../respan/python-sdks/respan-tracing \
            -e ../../../../respan/python-sdks/respan \
            -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-openinference \
            -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-autogen
```

Required root `.env` values:

```bash
RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
RESPAN_BASE_URL="https://api.respan.ai/api"
RESPAN_MODEL="gpt-4o-mini"
```

`RESPAN_BASE_URL` and `RESPAN_MODEL` are optional. The examples route model
calls through the Respan OpenAI-compatible gateway, so no separate OpenAI key is
required.

## Examples

| Example | Description |
|---------|-------------|
| `01_assistant_run.py` | Single AutoGen assistant run with Respan attributes |
| `02_tool_use.py` | Assistant run that must call a Python tool |
| `03_round_robin_team.py` | Multi-agent round-robin team conversation |

Run any example:

```bash
python 01_assistant_run.py
```

## How it works

1. `Respan` initializes the OpenTelemetry export pipeline.
2. `AutoGenInstrumentor()` activates the OpenInference AutoGen AgentChat
   instrumentor through Respan's OpenInference translator.
3. `OpenAIChatCompletionClient` points at the Respan gateway using the same
   `RESPAN_API_KEY`.
4. Agent, team, tool, and LLM spans are exported to Respan.
