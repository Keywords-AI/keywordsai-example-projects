# AgentSpec Respan Tracing Examples

These examples run AgentSpec (`pyagentspec`) through Respan tracing using
`respan-instrumentation-agentspec`.

The scripts load API keys from the repo-root `.env`. They route AgentSpec's
OpenAI-compatible LLM calls through the Respan gateway, so `RESPAN_API_KEY` or
`RESPAN_GATEWAY_API_KEY` is enough.

## Setup

```bash
cd python/tracing/agentspec
pip install -r requirements.txt
```

For local instrumentation development:

```bash
pip install -e /home/yuyang/KeywordsAI/respan/python-sdks/respan \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-tracing \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/instrumentations/respan-instrumentation-openinference \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/instrumentations/respan-instrumentation-agentspec
```

## Examples

| Example | Description |
| --- | --- |
| `01_haiku_agent.py` | Basic AgentSpec LangGraph agent run (`agentspec_haiku_agent`) |
| `02_agent_with_tool.py` | AgentSpec `ServerTool` mapped to a Python tool registry (`agentspec_tool_agent`) |
| `03_propagated_attributes.py` | Customer, thread, metadata, and environment propagation (`agentspec_propagated_attributes`) |

Run an example:

```bash
python 01_haiku_agent.py
```
