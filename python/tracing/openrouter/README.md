# OpenRouter Python tracing examples

These examples trace OpenRouter-style OpenAI-compatible Python client usage with
`respan-instrumentation-openrouter`.

The committed suite targets OpenAI Python `>=3.0.0,<4.0.0`, matching the
instrumentation package's tested delegate surface.

## Covered examples

- `01_chat_completion.py` - sync chat completion
- `02_streaming_chat.py` - streaming chat completion
- `03_tool_calling.py` - tool definitions, model tool call, and traced local tool
- `04_async_chat.py` - async chat completion
- `05_structured_output.py` - JSON structured output
- `06_async_streaming_chat.py` - async streaming and final usage
- `07_expected_error.py` - deterministic expected HTTP 429
- `08_live_provider.py` - optional credential-gated live OpenRouter response

Run all examples:

```bash
python -m pip install -r python/tracing/openrouter/requirements.txt
python python/tracing/openrouter/run_all.py
```

For a marker-scoped platform validation run:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-fix-py-group-21-<timestamp> \
  python python/tracing/openrouter/run_all.py
```

Each child process has a 90-second timeout and explicitly closes its OpenAI
client, flushes Respan, and shuts down its instrumentation lifecycle.

For local instrumentation validation, install only the OpenRouter source package
as an editable link after the registry-portable requirements. The released
OpenAI delegate remains installed from the registry so this suite does not
silently depend on another unmerged instrumentation checkout:

```bash
RESPAN_REPO=../respan
python -m pip install --no-deps -e \
  "$RESPAN_REPO/python-sdks/instrumentations/respan-instrumentation-openrouter"
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

Examples `01` through `07` always use the local OpenAI-compatible mock, even when
live credentials are present. This keeps their output, errors, stream protocol,
and usage deterministic while still exercising the OpenAI-compatible SDK path,
the OpenRouter instrumentor, and Respan export. Example `08` explicitly opts
into the real provider.

`07_expected_error.py` always uses the local mock so the precise 429 path is
deterministic. `08_live_provider.py` runs only when `OPENROUTER_API_KEY` is set.
