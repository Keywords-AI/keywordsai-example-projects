# Writer tracing examples

Examples for `respan-instrumentation-writer` with the official `writerai` SDK.
They load `.env` from the `respan-example-projects` repo root.

## Setup

```bash
pip install -r python/tracing/writer/requirements.txt
```

Required for Respan export:

```bash
RESPAN_API_KEY=...
RESPAN_BASE_URL=https://api.respan.ai/api
```

Optional for live Writer API calls:

```bash
WRITER_API_KEY=...
WRITER_MODEL=palmyra-x5
WRITER_VISION_MODEL=palmyra-vision
WRITER_TRANSLATION_MODEL=palmyra-translate
WRITER_GRAPH_ID=...
WRITER_APPLICATION_ID=...
WRITER_FILE_ID=...
```

When `WRITER_API_KEY` is absent, the examples use a local `httpx.MockTransport`.
Mock mode still runs the actual Writer SDK methods and exports real Respan spans,
so it is useful for instrumentation verification in this checkout.

## Run

```bash
python python/tracing/writer/run_all.py
```

Or run one script directly:

```bash
python python/tracing/writer/01_chat_completion.py
```

## Covered features

- `client.chat.chat()`
- `client.chat.stream()`
- `client.chat.parse()` structured responses
- function tool-call request/response capture
- `client.completions.create()` and streamed completions
- `AsyncWriter.chat.chat()`
- `client.graphs.question()`
- `client.applications.generate_content()` and streamed application output
- `client.vision.analyze()`
- `client.translation.translate()`
- `client.tools.web_search()` and `client.tools.parse_pdf()`
