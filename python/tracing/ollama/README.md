# Ollama Tracing Examples

Runnable examples for `respan-instrumentation-ollama`.

The examples load Respan credentials from the repo-root `.env`. If `OLLAMA_HOST` is set, they use that Ollama server. If `OLLAMA_HOST` is unset, the examples start a small local Ollama-compatible server so tracing can be validated without a local model daemon.

## Run

```bash
cd python/tracing/ollama
python 01_chat.py
python 02_stream_generate.py
python 03_tool_calling.py
python 04_embeddings.py
```

Each script prints `workflow_name` and `custom_identifier` so the exported trace can be found in Respan.
