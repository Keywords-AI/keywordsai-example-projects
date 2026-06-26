# Together AI TypeScript Tracing Examples

Examples for `@respan/instrumentation-together-ai`. The scripts load `.env` from the `respan-example-projects` repo root.

Required environment variables:

- `RESPAN_API_KEY`
- `TOGETHER_API_KEY`

Optional model overrides:

- `TOGETHER_CHAT_MODEL`
- `TOGETHER_COMPLETION_MODEL`
- `TOGETHER_EMBEDDING_MODEL`
- `TOGETHER_IMAGE_MODEL`
- `TOGETHER_RERANK_MODEL`
- `TOGETHER_SPEECH_MODEL`
- `TOGETHER_SPEECH_VOICE`
- `TOGETHER_TRANSCRIPTION_MODEL`

Run all examples:

```bash
npm run examples
```

When `TOGETHER_API_KEY` is absent, `npm run examples` starts a local mock Together-compatible server so the SDK and Respan instrumentation paths can still be validated end to end. Set `TOGETHER_EXAMPLE_DISABLE_MOCK=1` to require a real Together API key.
