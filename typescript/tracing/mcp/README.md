# MCP + Respan Examples (TypeScript)

Runnable examples for tracing Model Context Protocol client and server tool operations with Respan.

These examples load environment variables from the repository root `.env` file.

## Setup

```bash
cd typescript/tracing/mcp
npm install
```

Required root `.env` value:

| Variable | Required | Description |
| --- | --- | --- |
| `RESPAN_API_KEY` | Yes | Respan API key for trace export. |
| `RESPAN_BASE_URL` | No | Defaults to Respan production API. |
| `RESPAN_EXAMPLE_RUN_ID` | No | Optional run id for exact trace lookup. |

## Run

```bash
npm run all
```

Individual scripts:

- `01_client_tool_call.ts`: list tools and call a registered MCP tool.
- `02_resources_and_prompts.ts`: list/read MCP resources and prompts.
- `03_legacy_tool_api.ts`: trace the legacy `server.tool()` API.

Each script prints a workflow name and run id that can be used to find the trace in Respan.
