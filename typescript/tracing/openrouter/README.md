# OpenRouter TypeScript tracing examples

These examples exercise the Respan OpenRouter TypeScript instrumentation:

- `01_chat_completion.ts`: non-streaming chat completion
- `02_tool_calling.ts`: tool-calling request/response capture
- `03_streaming.ts`: streamed chat completion aggregation
- `04_embeddings.ts`: embeddings span without exporting vectors

Run from this directory after setting `RESPAN_API_KEY` and `OPENROUTER_API_KEY` in the `respan-example-projects/.env` file:

```bash
npm install
npm run examples
```

Each run prints a shared `runId`; Respan spans also include `custom_identifier`, `trace_group_identifier`, and `metadata.run_id` for MCP lookup.
