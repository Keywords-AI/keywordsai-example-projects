# Respan MCP Instrumentation Examples

Runnable examples for `respan-instrumentation-mcp`.

The examples load `RESPAN_API_KEY` from the repo root `.env` file and export traces to Respan. Each client script wraps its MCP session in a stable workflow name and uses the same value as `trace_group_identifier`, so traces can be found by workflow name. Set `RESPAN_EXAMPLE_RUN_ID` to attach one exact batch marker to every example while retaining a separate per-example invocation ID.

The current examples support MCP Python SDK 1.27 or newer on the 1.x line.
MCP 2.x removed the `mcp.server.fastmcp` API used by this server and is not yet
supported.

## Setup

```bash
cd python/tracing/mcp
pip install -r requirements.txt
```

For local development against this checkout:

```bash
RESPAN_REPO=/path/to/respan
pip install -e "$RESPAN_REPO/python-sdks/respan-sdk" \
            -e "$RESPAN_REPO/python-sdks/respan-tracing" \
            -e "$RESPAN_REPO/python-sdks/respan" \
            -e "$RESPAN_REPO/python-sdks/instrumentations/respan-instrumentation-openinference" \
            -e "$RESPAN_REPO/python-sdks/instrumentations/respan-instrumentation-mcp" \
            "mcp>=1.27,<2" python-dotenv
```

## Examples

| Example | Workflow name | Description |
|---------|---------------|-------------|
| `01_tool_call_workflow.py` | `mcp_tool_call_workflow` | Lists tools and calls `summarize_city`. |
| `02_resource_read_workflow.py` | `mcp_resource_read_workflow` | Lists resources and reads `profile://city/paris`. |
| `03_prompt_fetch_workflow.py` | `mcp_prompt_fetch_workflow` | Lists prompts and fetches `city_research_prompt`. |
| `04_connection_failure_workflow.py` | `mcp_connection_failure_workflow` | Records a deliberate startup failure with diagnostic content. |

Run an example:

```bash
RESPAN_EXAMPLE_RUN_ID=mcp-audit-001 python 01_tool_call_workflow.py
```
