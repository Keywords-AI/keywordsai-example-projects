# Mastra + Respan Tracing Examples

Runnable Mastra TypeScript examples using `@respan/instrumentation-mastra`.

## Setup

These examples load environment variables from the repository root `.env` file.

```bash
cd typescript/tracing/mastra
npm install
npm run examples
```

Required root `.env` values:

| Variable | Required | Description |
| --- | --- | --- |
| `RESPAN_API_KEY` | Yes | Used for Respan tracing and the Respan gateway. |
| `RESPAN_BASE_URL` | No | Defaults to `https://api.respan.ai/api`. |
| `MASTRA_EXAMPLE_MODEL` | No | Defaults to `gpt-4.1-nano` through the OpenAI-compatible gateway. |
| `RESPAN_EXAMPLE_RUN_ID` | No | Custom run id used in metadata and console output. |

The examples set `OPENAI_API_KEY` from `RESPAN_API_KEY` and `OPENAI_BASE_URL` from `RESPAN_BASE_URL`, so no separate provider key is required.

## Scripts

- `npm run example:basic` - simple agent generation.
- `npm run example:tool` - agent with a local weather tool.
- `npm run example:stream` - streaming agent response.
- `npm run examples` - run the complete set.

Each script emits a readable workflow name such as `Mastra Tool Example.workflow`, sets the same value as `trace_group_identifier`, and includes the run id in metadata so traces are easy to find in Respan.
