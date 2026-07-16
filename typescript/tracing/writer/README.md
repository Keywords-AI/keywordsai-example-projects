# Writer TypeScript Tracing Examples

Runnable examples for `@respan/instrumentation-writer` and the official `writer-sdk`.

The examples load `.env` from the `respan-example-projects` repo root. By default they use a deterministic mock `fetch` with the real Writer SDK so the examples run without a Writer API key and still send Respan traces. Set `WRITER_EXAMPLE_MODE=live` and `WRITER_API_KEY` to use the live Writer API.

```bash
npm install
npm run examples
```

Coverage:

- basic chat completion
- streaming chat completion
- structured output through `chat.parse`
- custom tool call and tool-result round trip
- text completion
- deterministic expected error
