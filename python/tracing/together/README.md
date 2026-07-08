# Together AI tracing examples

These examples exercise `respan-instrumentation-together` against the official
Together Python SDK.

## Setup

From this directory:

```bash
uv venv
uv pip install -r requirements.txt
```

The examples load `/home/yuyang/KeywordsAI/respan-example-projects/.env`.
They use `TOGETHER_API_KEY` directly when present. Otherwise they use
`RESPAN_GATEWAY_API_KEY` or `RESPAN_API_KEY` with `RESPAN_GATEWAY_BASE_URL` or
`RESPAN_BASE_URL`.

Optional model overrides:

- `RESPAN_TOGETHER_MODEL`
- `RESPAN_TOGETHER_COMPLETION_MODEL`
- `RESPAN_TOGETHER_EMBEDDING_MODEL`
- `RESPAN_TOGETHER_RERANK_MODEL`
- `RESPAN_TOGETHER_IMAGE_MODEL`

## Run

```bash
python 01_chat_completion.py
python 02_stream_chat.py
python 03_async_chat.py
python 04_text_completion.py
python 05_embeddings.py
python 06_rerank.py
python 07_image_generation.py
python 08_tool_calling.py
```
