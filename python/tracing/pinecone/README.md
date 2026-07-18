# Pinecone Tracing Example

This example traces a concise `describe_index_stats` -> `upsert` -> `fetch` ->
`query` flow against an existing dense-vector Pinecone index. It never creates,
configures, or deletes an index, and it cleans up only the unique IDs written by
the current run.

Add these values to the repo-root `.env`:

```dotenv
RESPAN_API_KEY=...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=your-existing-index
# Recommended when known; avoids resolving the host by index name.
PINECONE_INDEX_HOST=your-index-host
```

The emitted workflow name is `pinecone_upsert_and_query_workflow`.

## Run

```bash
cd python/tracing/pinecone
pip install -r requirements.txt
python run_all.py
```

Set `PINECONE_INGEST_TIMEOUT_SECONDS` to change the default 30-second fetch
polling window. When running before the instrumentor is published, include its
local `src` directory and the local Respan packages on `PYTHONPATH`.
