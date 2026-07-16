# Cohere tracing examples

These examples exercise `respan-instrumentation-cohere` with Cohere chat, streaming chat, embeddings, and rerank.

## Environment

The scripts load `respan-example-projects/.env`.

Required:

- `RESPAN_API_KEY`

Optional:

- `RESPAN_BASE_URL`
- `CO_API_KEY` or `COHERE_API_KEY`
- `COHERE_CHAT_MODEL`
- `COHERE_EMBED_MODEL`
- `COHERE_RERANK_MODEL`
- `COHERE_USE_STUBS`
- `RESPAN_EXAMPLE_RUN_ID`

When no Cohere key is present, the examples patch the Cohere SDK with local stub methods before Respan instrumentation is activated. This keeps the examples runnable while still exercising the Cohere SDK wrapper path and exporting spans to Respan.

## Run

```bash
python python/tracing/cohere/run_all_examples.py
```

Each script sets a stable workflow name:

- `cohere_chat.workflow`
- `cohere_streaming_chat.workflow`
- `cohere_embed_rerank.workflow`
