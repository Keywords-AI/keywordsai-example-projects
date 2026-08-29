# OpenAI SDK tracing examples

These 18 scripts exercise the real OpenAI 3.x sync and async client surfaces
while exporting traces through the local editable Respan packages. The default
mode is deterministic: an in-process `httpx2.MockTransport` supplies valid
OpenAI response payloads, so no provider credential or managed prompt is
required. Requests still pass through the official OpenAI resource, streaming,
SSE, Pydantic parse, and error classes.

The examples cover Chat and Responses calls, sync/async structured parsing,
streaming, two-turn tools, embeddings, precise 401 handling, propagated
attributes, decorators, prompt-shaped requests, and deterministic batch result
logging.

## Run

From this directory, link the checked-out packages and run the full set with
one exact marker:

```bash
python -m pip install -e ../../../../respan/python-sdks/respan-sdk \
  -e ../../../../respan/python-sdks/respan-tracing \
  -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-openai \
  -e ../../../../respan/python-sdks/respan
RESPAN_EXAMPLE_RUN_ID=openai-check-001 python run_all.py
```

`run_all.py` preserves a shell-supplied marker, runs every script independently,
and reports all failures after the set finishes. Every script flushes and shuts
down Respan explicitly.

## Optional live provider

Set the following only when you want to replace deterministic transport with a
real OpenAI-compatible endpoint:

```bash
RESPAN_OPENAI_LIVE=1
OPENAI_API_KEY=...
# Optional:
OPENAI_BASE_URL=https://api.openai.com/v1
```

Managed-prompt-shaped examples use `RESPAN_PROMPT_ID` when supplied. Batch
examples intentionally use deterministic result payloads because provider-side
file upload and polling are independent of this instrumentation package.
