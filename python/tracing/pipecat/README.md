# Pipecat tracing

These examples validate `respan-instrumentation-pipecat` with Pipecat's current
`PipelineWorker` and `WorkerRunner` lifecycle.

- `01_offline_pipeline.py` runs a deterministic real Pipecat pipeline.
- `02_gateway_llm_pipeline.py` uses Pipecat's real OpenAI service through the
  configured Respan gateway (and has a deterministic fallback if gateway
  configuration is absent).
- `03_expected_error.py` emits a deterministic provider-style 401 `ErrorFrame`.

From this directory:

```bash
python -m pip install -r requirements.txt
RESPAN_EXAMPLE_RUN_ID=pipecat-check python run_all.py
```

For local instrumentation development, link the package after installing the
registry requirements:

```bash
python -m pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-pipecat
```

The runner preserves the exact shell marker, runs every committed scenario,
continues after failures/timeouts, and reports an aggregate result. Every
script flushes and shuts down Respan explicitly.
