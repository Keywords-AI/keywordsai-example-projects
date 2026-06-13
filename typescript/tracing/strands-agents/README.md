# Strands Agents + Respan Tracing Examples

Runnable Strands Agents TypeScript examples using `@respan/instrumentation-strands-agents`.

## Setup

These examples load environment variables from the repository root `.env` file.

```bash
cd typescript/tracing/strands-agents
npm install
npm run all
```

Required root `.env` values:

| Variable | Required | Description |
| --- | --- | --- |
| `RESPAN_API_KEY` | Yes | Used for Respan trace export. |
| `RESPAN_BASE_URL` | No | Defaults to `https://api.respan.ai/api`. |
| `RESPAN_EXAMPLE_RUN_ID` | No | Custom run id used in metadata and console output. |

The examples use deterministic Strands model providers so they exercise Strands agent, model, tool, structured output, graph, swarm, streaming, and MCP paths without requiring a separate model-provider key.

## Scripts

- `npm run 01:basic` - basic agent invocation.
- `npm run 02:tool` - agent model-driven local tool call.
- `npm run 03:streaming` - streamed agent output.
- `npm run 04:structured` - structured output through the Strands structured-output tool.
- `npm run 05:graph` - graph orchestration with two agents.
- `npm run 06:swarm` - swarm orchestration with a structured handoff.
- `npm run 07:mcp` - Strands agent using an in-memory MCP tool.
- `npm run all` - run the complete set.

Each script emits a readable workflow name, sets the same value as `trace_group_identifier`, and includes the run id in metadata so traces are easy to find in Respan.
