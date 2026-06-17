# Cursor SDK tracing examples

These examples replay Cursor hook JSON payloads through `respan-instrumentation-cursor-sdk`. They load environment variables from the repository root `.env` file.

Required for exporting traces:

```bash
RESPAN_API_KEY=...
```

Optional environment variables:

```bash
RESPAN_BASE_URL=https://api.respan.ai/api
CURSOR_EXAMPLE_MODEL=claude-4-sonnet
CURSOR_EXAMPLE_VERSION=1.0.0
```

Run all scenarios:

```bash
python run_all.py
```

Or run one script at a time:

```bash
python 01_agent_turn.py
python 02_terminal_and_mcp_tools.py
python 03_stop_cleanup.py
python 04_full_hook_transcript.py
```

Each script prints a stable `workflow_name`:

- `cursor_sdk_agent_turn`
- `cursor_sdk_terminal_and_mcp_tools`
- `cursor_sdk_stop_cleanup`
- `cursor_sdk_full_transcript`

Use those workflow names to find the exported spans in Respan.
