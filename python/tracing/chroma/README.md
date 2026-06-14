# Chroma Tracing Examples

Runnable Chroma examples for Respan tracing. The scripts use the repo-root `.env` file and emit workflow-discoverable traces with these workflow names:

- `chroma_collection_lifecycle_workflow`
- `chroma_write_and_read_workflow`
- `chroma_query_and_filters_workflow`
- `chroma_update_upsert_delete_workflow`
- `chroma_propagated_attributes_workflow`

## Run

```bash
cd python/tracing/chroma
python run_all.py
```

When running from this checkout before the package is published, include the local Respan package paths on `PYTHONPATH`.
