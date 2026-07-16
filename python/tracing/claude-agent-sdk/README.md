# Claude Agent SDK + Respan Examples (Python)

Runnable examples showing how to trace Claude Agent SDK queries with Respan.

## Setup

```bash
cd python/tracing/claude-agent-sdk

# Install dependencies
pip install claude-agent-sdk opentelemetry-claude-agent-sdk respan-ai respan-instrumentation-claude-agent-sdk python-dotenv

# Copy and fill in your keys
cp .env.example .env
```

## Examples

### Basic

| File | Description |
|------|-------------|
| `basic/hello_world_test.py` | Simplest example: ask Claude a question and see the trace |
| `basic/wrapped_query_test.py` | Auto-instrumented `query()` helper pattern |

### Tools

| File | Description |
|------|-------------|
| `tools/tool_use_test.py` | Agent with tools (Read, Glob, Grep) and tool spans |
| `tools/multi_tool_test.py` | Agent using several tools in sequence |

### Streaming

| File | Description |
|------|-------------|
| `streaming/stream_messages_test.py` | Process each message type as it streams |

### Sessions

| File | Description |
|------|-------------|
| `sessions/multi_turn_test.py` | Multiple queries with session tracking |

## Run All Examples With Fake SDK Messages

This runner does not require `ANTHROPIC_API_KEY`; it patches the SDK query stream to verify Respan instrumentation.

```bash
python _run_all_examples.py
```

## Running With Pytest

```bash
pip install pytest pytest-asyncio
pytest basic/ tools/ streaming/ sessions/ -v
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RESPAN_API_KEY` | Yes | Your Respan API key |
| `ANTHROPIC_API_KEY` | Yes for live SDK calls | Your Anthropic API key |
| `RESPAN_BASE_URL` | No | Override ingest URL (default: `https://api.respan.ai/api`) |
