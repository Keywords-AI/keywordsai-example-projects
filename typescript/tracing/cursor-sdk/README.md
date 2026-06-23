# Cursor SDK + Respan Examples (TypeScript)

Runnable examples for tracing Cursor TypeScript SDK-compatible agent runs with Respan.

These examples load environment variables from the repository root `.env` file and use an in-process Cursor SDK-compatible module so the examples are deterministic while exercising the same public `Agent` and `Run` APIs that `@cursor/sdk` exposes.

## Setup

```bash
cd typescript/tracing/cursor-sdk
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

- `01_agent_prompt.ts`: traces `Agent.prompt()` summary spans.
- `02_agent_stream.ts`: traces `Agent.create()`, `SDKAgent.send()`, `Run.stream()`, callbacks, MCP server config, thinking/status/task events, and tool-call stream messages.
- `03_custom_tools.ts`: traces local `customTools` execution and `Run.wait()`.

Each script prints a workflow name and run id that can be used to find the trace in Respan.
