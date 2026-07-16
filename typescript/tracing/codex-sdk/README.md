# Respan Codex SDK TypeScript Examples

Examples for tracing the OpenAI Codex TypeScript SDK with Respan.

The examples load `.env` from the `respan-example-projects` repo root and use
`RESPAN_API_KEY` for tracing. Codex auth uses `CODEX_API_KEY` when set, otherwise
`OPENAI_API_KEY`.

```bash
npm install
npm run examples
```

Scripts:

- `01:basic` - buffered `Thread.run()` turn
- `02:streaming` - streamed `Thread.runStreamed()` events
- `03:structured` - JSON schema output
- `04:image` - structured text plus local image input
- `05:resume` - two turns on one thread
- `06:file-change` - scratch workspace file change
- `07:error` - expected startup failure instrumentation
