# Qdrant OTel 2.x tracing examples

The deterministic example set uses the real current `qdrant-client` local mode and covers synchronous CRUD/query operations, asynchronous operations, and a deliberate missing-collection error. It does not require a hosted Qdrant credential.

```bash
pip install -r requirements.txt
python run_all.py
```

For local instrumentation development, install the Qdrant instrumentation and Respan core packages editable from the sibling `respan` checkout. The committed requirements stay registry-portable.

Every process preserves one shell-supplied `RESPAN_EXAMPLE_RUN_ID`, records it as both `example_run_id` and `run_id`, closes its client, flushes/shuts down Respan, and returns bounded semantic workflow results.
