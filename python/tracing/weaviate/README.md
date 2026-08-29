# Weaviate tracing examples

The first three scenarios use the installed Weaviate 4.x manager classes with a
deterministic local backend, so activation, sync/async wrappers, canonical
operation fields, vector content, expected failure, exact marker propagation,
and shutdown are repeatable without a service.

```bash
pip install -r python/tracing/weaviate/requirements.txt
RESPAN_EXAMPLE_RUN_ID=otel2-weaviate-check python python/tracing/weaviate/run_all.py
```

The operation remains a canonical `task`; `traceloop.entity.name` and
`db.operation` retain the precise collection/data/query identity.
`04_live_service.py` performs a temporary create/insert/query/delete round trip
when `WEAVIATE_URL` and `WEAVIATE_API_KEY` are set, and otherwise exits with a
clean credential-gated skip.
