# Google GenAI tracing examples

These examples trace the official `google-genai` Python SDK with Respan. They load environment variables from the repository root `.env` file.

Required for exporting traces:

```bash
RESPAN_API_KEY=...
```

For Gemini calls, use one of these options:

```bash
# Direct Google API calls, still traced to Respan
GOOGLE_API_KEY=...
# or
GEMINI_API_KEY=...
```

If neither Google key is set, the examples route through the Respan Gemini gateway with `RESPAN_API_KEY`. That requires Gemini provider credentials or managed credits configured on the Respan account.

Optional environment variables:

```bash
RESPAN_BASE_URL=https://api.respan.ai/api
RESPAN_GOOGLE_GENAI_MODEL=gemini-2.5-flash
```

Run one script at a time:

```bash
python 01_generate_content.py
python 02_stream_content.py
python 03_async_generate_content.py
python 04_tool_calling.py
```

Each script prints both a `custom_identifier` and `workflow_name`. The workflow name is also used as the Respan trace group identifier so the run is easy to find in traces and MCP lookups.
