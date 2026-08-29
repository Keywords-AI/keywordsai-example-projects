# Groq tracing examples

These examples trace the official `groq` Python SDK with Respan. They load
environment variables from the repository root `.env` file.

Required for exporting traces and gateway calls:

```bash
RESPAN_API_KEY=...
```

Optional environment variables:

```bash
RESPAN_BASE_URL=https://api.respan.ai/api
RESPAN_GROQ_MODEL=gpt-4.1-nano
GROQ_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=...
```

If `GROQ_API_KEY` is set, the examples call Groq directly and default to
`GROQ_MODEL=llama-3.1-8b-instant`. Otherwise they route the Groq SDK through
the Respan gateway with `RESPAN_API_KEY` and default to `RESPAN_GROQ_MODEL=gpt-4.1-nano`,
which works without separate Groq provider credentials. The gateway path is
adapted in the example HTTP client so the official Groq SDK remains the
instrumented client.

Run one script at a time:

```bash
python 01_chat_completion.py
python 02_streaming.py
python 03_tool_calling.py
python run_all.py
```

Each script prints both a `custom_identifier` and `workflow_name`. The workflow
name is also used as the Respan trace group identifier so the run is easy to
find in traces and MCP lookups. Set `RESPAN_EXAMPLE_RUN_ID` to attach one exact
batch marker to all three scenarios.
