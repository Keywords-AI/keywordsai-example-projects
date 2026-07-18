# LanceDB Tracing Example

This offline quickstart creates a temporary local LanceDB table, adds documents,
runs vector search, and emits a Respan trace named
`lancedb_local_vector_search_workflow`.

## Run

Add `RESPAN_API_KEY` to the repository-root `.env`, then run:

```bash
cd python/tracing/lancedb
pip install -r requirements.txt
python 01_quickstart.py
```

The temporary database is removed after the workflow finishes.
