# Azure OpenAI + Respan Examples (TypeScript)

Runnable examples for tracing Azure OpenAI TypeScript client calls with Respan.

These examples load environment variables from the repository root `.env` file.
They use the real `openai` `AzureOpenAI` client surface with deterministic mock
responses, so they can be run without Azure credentials while still exporting
real traces to Respan.

## Setup

```bash
cd typescript/tracing/azure-openai
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

- `01_chat_completion.ts`: trace a standard Azure chat completion.
- `02_streaming_tool_calls.ts`: trace streaming tool-call deltas, the executed `lookup_city` tool span, and the final assistant answer after the tool result is sent back to Azure OpenAI.
- `03_text_completion.ts`: trace a legacy text completion call.
- `04_embeddings.ts`: trace an embeddings call without exporting vectors.

Each script prints a workflow name and run id that can be used to find the trace in Respan.
