# Together OTel 2.x tracing examples

The nine examples exercise the official Together Python SDK with the local
Respan instrumentation. By default, the SDK parses deterministic
`httpx.MockTransport` responses, so chat, streaming, text completion,
embeddings, rerank, image, connected tool execution, and a provider 429 are
repeatable without a Together credential.

Set `RESPAN_TOGETHER_LIVE=1` and `TOGETHER_API_KEY` to make the non-error
examples call Together directly. The exact `RESPAN_EXAMPLE_RUN_ID` supplied by
the caller is preserved in both `run_id` and `example_run_id` metadata.

## Registry setup

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

For local instrumentation development, link the sibling checkout after the
registry install:

```bash
.venv/bin/pip install --no-build-isolation --no-deps -e \
  ../../../../respan/python-sdks/instrumentations/respan-instrumentation-together
```

## Run the complete set

```bash
RESPAN_EXAMPLE_RUN_ID=my-exact-marker .venv/bin/python run_all.py
```

`run_all.py` applies one marker to every subprocess, bounds each process with a
timeout, continues after failures, and returns nonzero if any example fails.
