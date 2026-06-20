# Superagent + Respan Examples (TypeScript)

Runnable examples for tracing Superagent `safety-agent` guardrail, redaction,
and scan operations with Respan.

These examples load environment variables from the repository root `.env` file.

## Setup

```bash
cd typescript/tracing/superagent
npm install
```

Required root `.env` value:

| Variable | Required | Description |
| --- | --- | --- |
| `RESPAN_API_KEY` | Yes | Respan API key for trace export. |
| `RESPAN_BASE_URL` | No | Defaults to Respan production API. |
| `RESPAN_GATEWAY_API_KEY` | No | Defaults to `RESPAN_API_KEY` for OpenAI-compatible Superagent provider calls. |
| `RESPAN_GATEWAY_BASE_URL` | No | Defaults to `RESPAN_BASE_URL`. |
| `SUPERAGENT_API_KEY` | No | Defaults to a local example value for SDK usage tracking. |
| `SUPERAGENT_MODEL` | No | Defaults to `RESPAN_MODEL` or `openai-compatible/gpt-4o-mini`. |
| `RESPAN_EXAMPLE_RUN_ID` | No | Optional run id for exact trace lookup. |
| `DAYTONA_API_KEY` | No | Required only for the live repository scan example. |

## Run

```bash
npm run all
```

Individual scripts:

- `01_guard.ts`: classify prompt-injection style input with `guard()`.
- `02_redact.ts`: redact email and phone data with `redact()`.
- `03_workflow.ts`: run `guard()` and `redact()` inside nested Respan workflow/task spans.
- `04_scan.ts`: run `scan()` when Daytona credentials are available; otherwise emit a skipped workflow result.

Each script prints a workflow name and run id that can be used to find the trace in Respan.
