# Milvus Tracing Examples

Runnable Respan tracing examples for `MilvusClient`. They use an isolated local
Milvus Lite database, so no Milvus server or provider credential is required.
The repo-root `.env` must contain `RESPAN_API_KEY`.

The examples use an explicit collection schema so the current PyMilvus and
Milvus Lite pair avoids the unsupported automatic index timestamp probe. The
emitted workflow names are:

- `milvus_collection_lifecycle_workflow`
- `milvus_data_operations_workflow`
- `milvus_expected_error_workflow`

## Run

```bash
cd python/tracing/milvus
pip install -r requirements.txt
python run_all.py
```

When running before the instrumentor is published, include its local `src`
directory and the local Respan packages on `PYTHONPATH`.
