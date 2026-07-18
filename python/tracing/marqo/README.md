# Marqo Tracing Example

This quickstart creates a temporary Marqo index, adds documents, runs tensor
search, and emits a Respan trace named `marqo_document_search_workflow`.

## Run

Start a compatible Marqo instance, add `RESPAN_API_KEY` to the repository-root
`.env`, then run:

```bash
cd python/tracing/marqo
pip install -r requirements.txt
python 01_quickstart.py
```

`MARQO_URL` defaults to `http://localhost:8882`. For Marqo Cloud, set
`MARQO_URL` and `MARQO_API_KEY` in the same `.env` file. The example deletes its
uniquely named index before exiting.
