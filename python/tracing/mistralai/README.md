# Mistral AI tracing examples

These examples trace the official `mistralai` Python SDK with Respan. They load
environment variables from the repository root `.env` file.

Required for exporting traces:

```bash
RESPAN_API_KEY=...
```

For Mistral calls, use one of these options:

```bash
# Direct Mistral API calls, still traced to Respan
MISTRAL_API_KEY=...
```

If `MISTRAL_API_KEY` is not set, the examples route the Mistral SDK through the
Respan OpenAI-compatible gateway using `RESPAN_GATEWAY_API_KEY` or
`RESPAN_API_KEY`. In gateway mode, `RESPAN_MISTRALAI_MODEL` is used when set;
otherwise the scripts fall back to `RESPAN_MODEL` from the repo-root `.env` so
the examples run in this repository without requiring separate Mistral provider
credentials.

Optional environment variables:

```bash
RESPAN_BASE_URL=https://api.respan.ai/api
RESPAN_MISTRALAI_MODEL=mistral/mistral-small
MISTRALAI_MODEL=mistral/mistral-small
```

Run one script at a time:

```bash
python 01_chat_completion.py
python 02_multi_turn_chat.py
python 03_async_chat_completion.py
```

Each script prints both a `custom_identifier` and `workflow_name`. The workflow
name is also used as the Respan trace group identifier so the run is easy to
find in traces and MCP lookups.
