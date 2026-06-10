# Portkey tracing examples

These examples trace the official `portkey-ai` Python SDK with Respan. They load environment variables from the repository root `.env` file.

Required for exporting traces:

```bash
RESPAN_API_KEY=...
```

For Portkey calls, use one of these options:

```bash
# Direct Portkey Gateway calls
PORTKEY_API_KEY=...
PORTKEY_PROVIDER=@your-provider
# or
PORTKEY_CONFIG=pc-...
```

If `PORTKEY_API_KEY` is not set, the examples use a local OpenAI-compatible test endpoint so traces are runnable without third-party model credentials. To force a live provider fallback, set one of these in the root `.env` file:

```bash
PORTKEY_EXAMPLE_USE_OPENAI=1
OPENAI_API_KEY=...
# or
PORTKEY_EXAMPLE_USE_LIVE_GATEWAY=1
RESPAN_GATEWAY_API_KEY=...
RESPAN_GATEWAY_BASE_URL=...
```

Optional environment variables:

```bash
RESPAN_BASE_URL=https://api.respan.ai/api
PORTKEY_BASE_URL=https://api.portkey.ai/v1
PORTKEY_MODEL=gpt-4o-mini
RESPAN_MODEL=gpt-4.1-nano
```

Run one script at a time:

```bash
python 01_chat_completion.py
python 02_async_chat_completion.py
```

Each script prints both a `custom_identifier` and `workflow_name`. The workflow name is also used as the Respan trace group identifier so the run is easy to find in traces and MCP lookups.
