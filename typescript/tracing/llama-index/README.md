# LlamaIndex TypeScript tracing

These examples use `@respan/instrumentation-llama-index` with LlamaIndex.TS.

The scripts load environment variables from the repository root `.env`.

Required:

- `RESPAN_API_KEY`

By default the examples route LlamaIndex OpenAI calls through the Respan gateway
with `RESPAN_API_KEY`. To call OpenAI directly, set
`LLAMA_INDEX_USE_OPENAI_DIRECT=true` and provide `OPENAI_API_KEY`.

Run:

```bash
npm install --package-lock=false
npm run all
```

Each example uses a stable workflow name:

- `llama_index_ts_basic_llm`
- `llama_index_ts_rag_query_engine`
- `llama_index_ts_tool_call`

Those names are also used as trace group identifiers so the runs are easy to
find in Respan.

The tool-call workflow records the tool-selection chat span, the tool execution
span, and a final-answer chat span with the response text.
