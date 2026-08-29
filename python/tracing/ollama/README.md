# Ollama Tracing Examples

Runnable examples for `respan-instrumentation-ollama`.

The examples load Respan credentials from the repo-root `.env`. If `OLLAMA_HOST` is set, they use that Ollama server. If `OLLAMA_HOST` is unset, the examples start a small local Ollama-compatible server so tracing can be validated without a local model daemon.

## Run

```bash
cd python/tracing/ollama
RESPAN_EXAMPLE_RUN_ID=otel2-fix-py-group-NN-YYYYMMDDTHHMMSSZ python run_all.py
```

`run_all.py` preserves the exact invocation `RESPAN_EXAMPLE_RUN_ID`, runs all five scripts in isolated processes, reports every exit code, and fails after the suite if any script fails. Each script records that marker as `example_run_id` and prints it together with a unique per-case `custom_identifier`, so the exported traces can be queried as one batch without losing scenario identity.

The tool-calling example executes one `@tool`-decorated `get_weather` function between its two Ollama chat turns. The expected-error example always uses the local compatibility server and verifies an HTTP 503 span.
