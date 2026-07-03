# Claude Agent SDK + Respan Examples (Python)

Runnable examples showing how to trace Claude Agent SDK queries with Respan.

## Setup

```bash
cd python/tracing/anthropic-agents-sdk

# Install dependencies
pip install claude-agent-sdk opentelemetry-claude-agent-sdk respan-ai respan-instrumentation-claude-agent-sdk python-dotenv

# Copy and fill in your keys
cp .env.example .env
```

## Examples

### Basic

| File | Description |
|------|-------------|
| `basic/hello_world_test.py` | Simplest example — ask Claude a question, see the trace |
| `basic/wrapped_query_test.py` | One-liner integration using `exporter.query()` |

### Tools

| File | Description |
|------|-------------|
| `tools/tool_use_test.py` | Agent with tools (Read, Glob, Grep) — tool spans in trace |
| `tools/multi_tool_test.py` | Multi-turn agent using several tools in sequence |

### Streaming

| File | Description |
|------|-------------|
| `streaming/stream_messages_test.py` | Process each message type as it streams |

### Sessions

| File | Description |
|------|-------------|
| `sessions/multi_turn_test.py` | Multiple queries with session tracking |

### Gateway

Gateway examples have been moved to `python/gateway/anthropic-agents/`.

## Running with pytest

```bash
pip install pytest pytest-asyncio
pytest basic/ tools/ streaming/ sessions/ -v
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RESPAN_API_KEY` | Yes | Your Respan API key |
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `RESPAN_BASE_URL` | No | Override ingest URL (default: `https://api.respan.ai/api`) |
| `RESPAN_GATEWAY_BASE_URL` | No | Gateway URL; examples send Claude calls to `<value>/anthropic` |
| `RESPAN_GATEWAY_API_KEY` | No | Gateway key; falls back to `RESPAN_API_KEY` |
