# Pinecone tracing examples

These examples use the real Pinecone Python SDK and local editable Respan
instrumentation. Without Pinecone credentials they run against a bounded local
protocol fixture, so sync, async, success, and service-error paths remain
repeatable. When both `PINECONE_API_KEY` and `PINECONE_INDEX_NAME` are set, the
round-trip example uses that existing dense-vector index and deletes only its
own unique IDs.

## Setup

```bash
cd python/tracing/pinecone
pip install -r requirements.txt
```

For local instrumentation development, install the package from the sibling
checkout before running the examples:

```bash
pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-pinecone
```

Required in the repository-root `.env`:

```dotenv
RESPAN_API_KEY=...
```

Optional live Pinecone settings:

```dotenv
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=your-existing-index
PINECONE_INDEX_HOST=your-index-host
```

`PINECONE_INDEX_HOST` is required for the async live example. The expected-error
example always uses the deterministic fixture and never mutates a live index.

## Run

```bash
RESPAN_EXAMPLE_RUN_ID=my-exact-marker python run_all.py
```

The runner preserves the exact marker for all three processes, applies a
per-process timeout, continues after failures, and reports them together.
