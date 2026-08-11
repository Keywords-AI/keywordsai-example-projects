# BeeAI TypeScript Tracing Examples

Runnable examples for tracing BeeAI Framework with `@respan/instrumentation-beeai`.

The scripts load environment variables from the repository root `.env` file, then route BeeAI OpenAI adapter calls through the Respan OpenAI-compatible gateway.

The runtime passes both the application-loaded `beeai-framework` module and its
top-level `BeeAIInstrumentation` constructor to `BeeAIInstrumentor`. Keeping
those in the same dependency realm prevents linked workspace installs from
failing the upstream serializer's `instanceof ChatModel` checks.

## Setup

```bash
cd typescript/tracing/beeai
npm install
```

Required variables in `respan-example-projects/.env`:

| Variable | Description |
| --- | --- |
| `RESPAN_API_KEY` | Sends traces to Respan. |
| `RESPAN_GATEWAY_API_KEY` | Routes LLM calls through the Respan gateway. Falls back to `RESPAN_API_KEY`. |
| `RESPAN_GATEWAY_BASE_URL` | OpenAI-compatible gateway base URL. Defaults to `https://api.respan.ai/api`. |
| `RESPAN_MODEL` | Model routed through the gateway. Defaults to `gpt-4o`. |

## Scripts

```bash
npm run basic
npm run tools
npm run all
```

`01_basic_chat.ts` creates a `beeai_basic_chat.workflow` trace with one BeeAI OpenAI chat model call.

`02_tool_calling_agent.ts` creates a `beeai_tool_calling_agent.workflow` trace with a BeeAI tool-calling agent and calculator tool.

Each script sets `trace_group_identifier` and `metadata.workflow_name` to its workflow name, so the traces can be filtered by workflow name in Respan. Set `RESPAN_EXAMPLE_RUN_ID` to control the shared run id; otherwise the scripts generate one.
