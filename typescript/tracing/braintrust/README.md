# Braintrust + Respan TypeScript Examples

Runnable Braintrust TypeScript tracing examples using `@respan/instrumentation-braintrust`.

## Setup

These examples load environment variables from the repository root `.env` file.

```bash
cd typescript/tracing/braintrust
npm install
npm run examples
```

Required root `.env` values:

| Variable | Required | Description |
| --- | --- | --- |
| `RESPAN_API_KEY` | Yes | Used for Respan tracing and the Respan gateway. |
| `RESPAN_BASE_URL` | No | Defaults to `https://api.respan.ai/api`. |
| `BRAINTRUST_EXAMPLE_MODEL` | No | Defaults to `gpt-4.1-nano` through the OpenAI-compatible gateway. |
| `RESPAN_EXAMPLE_RUN_ID` | No | Custom run id used in metadata and console output. |

The set covers Braintrust LLM rows, task rows, tool rows, merge updates, scores,
tags, metrics, metadata, parent relationships, and error rows.
