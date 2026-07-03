# OpenAI Agents SDK Respan Examples

These examples use the current `respan-instrumentation-openai-agents` package. Older files still import `respan_exporter_openai_agents.RespanTraceProcessor`; the local compatibility bridge maps that import to the active instrumentation processor and initializes the unified Respan OTEL exporter.

## Setup

```bash
cd python/tracing/openai-agents-sdk
pip install openai-agents respan-ai respan-instrumentation-openai-agents python-dotenv pytest pytest-asyncio
```

Use the repository root `.env` values. OpenAI Agents 0.17 uses the Responses API by default. Because the current Respan OpenAI gateway covers chat-compatible routes, the local bridge forces `chat_completions` and routes model calls to `RESPAN_GATEWAY_BASE_URL` when `RESPAN_GATEWAY_API_KEY` is present. Set `RESPAN_OPENAI_AGENTS_USE_OPENAI=1` to use a direct `OPENAI_API_KEY`/Responses run instead. Traces always go to `RESPAN_BASE_URL` with `RESPAN_API_KEY`.

Run a focused example:

```bash
pytest basic/hello_world_test.py -q
pytest tools/functions_test.py -q
```
