# Vercel AI SDK TypeScript

Gateway-first examples for `ai@7.x` with `@respan/instrumentation-vercel`.

Set `RESPAN_API_KEY` in `respan-example-projects/.env`. Optional overrides: `RESPAN_GATEWAY_API_KEY`, `RESPAN_GATEWAY_BASE_URL`, `RESPAN_BASE_URL`, `RESPAN_MODEL`, `RESPAN_EMBEDDING_MODEL`.

Run:

```bash
npm install
npm run all
```

Examples:

- `01_generate_text.mjs`: `generateText` chat telemetry.
- `02_tool_call.mjs`: tool call loop with `stopWhen` and `prepareStep`.
- `03_embed.mjs`: single embedding call.
- `04_stream_text.mjs`: streaming text generation.
- `05_generate_object.mjs`: structured object generation.
- `06_embed_many.mjs`: batch embeddings.
- `07_tool_loop_agent.mjs`: `ToolLoopAgent` with a deterministic tool.
