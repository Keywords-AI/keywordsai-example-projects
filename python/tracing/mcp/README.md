# Respan MCP Instrumentation Examples

Runnable examples for `respan-instrumentation-mcp`.

The examples load `RESPAN_API_KEY` from the repo root `.env` file and export traces to Respan. Each client script wraps its MCP session in a stable workflow name and uses the same value as `trace_group_identifier`, so traces can be found by workflow name.

## Setup

```bash
cd python/tracing/mcp
pip install -r requirements.txt
```

For local development against this checkout:

```bash
pip install -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-sdk \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-tracing \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/respan \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/instrumentations/respan-instrumentation-openinference \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/instrumentations/respan-instrumentation-mcp \
            mcp python-dotenv
```

## Examples

| Example | Workflow name | Description |
|---------|---------------|-------------|
| `01_tool_call_workflow.py` | `mcp_tool_call_workflow` | Lists tools and calls `summarize_city`. |
| `02_resource_read_workflow.py` | `mcp_resource_read_workflow` | Lists resources and reads `profile://city/paris`. |
| `03_prompt_fetch_workflow.py` | `mcp_prompt_fetch_workflow` | Lists prompts and fetches `city_research_prompt`. |

Run an example:

```bash
python 01_tool_call_workflow.py
```
