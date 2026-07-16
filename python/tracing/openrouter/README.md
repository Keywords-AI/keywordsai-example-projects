# OpenRouter Python tracing examples

These examples trace OpenRouter-style OpenAI-compatible Python client usage with
`respan-instrumentation-openrouter`.

## Covered examples

- `01_chat_completion.py` - sync chat completion
- `02_streaming_chat.py` - streaming chat completion
- `03_tool_calling.py` - tool definitions, model tool call, and traced local tool
- `04_async_chat.py` - async chat completion
- `05_structured_output.py` - JSON structured output

Run all examples:

```bash
python python/tracing/openrouter/run_all.py
```

## Environment behavior

All scripts load `.env` from the `respan-example-projects` repo root.

Preferred live OpenRouter configuration:

```bash
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=openai/gpt-4o-mini
```

Optional Respan gateway mode:

```bash
OPENROUTER_USE_RESPAN_GATEWAY=true
RESPAN_GATEWAY_API_KEY=...
RESPAN_GATEWAY_BASE_URL=...
RESPAN_MODEL=...
```

If neither direct OpenRouter nor explicit gateway mode is configured, the
examples start a local OpenAI-compatible mock server. That keeps the example set
runnable in local CI while still exercising the OpenAI-compatible SDK path, the
OpenRouter instrumentor, and Respan export.
