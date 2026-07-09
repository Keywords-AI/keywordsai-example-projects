# Arize Phoenix + Respan Examples (TypeScript)

Runnable examples for tracing `@arizeai/phoenix-otel` OpenInference helpers with Respan.

These examples load environment variables from the repository root `.env` file.

## Setup

```bash
cd typescript/tracing/arize
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

- `01_trace_helpers.ts`: `traceAgent`, `traceChain`, `traceTool`, and context propagation.
- `02_manual_llm_attributes.ts`: `withSpan` plus rich LLM attribute builders.
- `03_retrieval_embedding_redaction.ts`: retriever, embedding, and redacted `OITracer` spans.
- `04_observe_decorator.ts`: `observe` decorators on class methods.

Each script prints a workflow name and run id that can be used to find the trace in Respan.
