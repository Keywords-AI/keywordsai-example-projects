# IBM watsonx.ai tracing examples

These examples trace the official `ibm-watsonx-ai` Python SDK with Respan. They load environment variables from the repository root `.env` file.

Required for exporting traces:

```bash
RESPAN_API_KEY=...
# or
RESPAN_GATEWAY_API_KEY=...
```

For live IBM watsonx.ai calls, set:

```bash
WATSONX_API_KEY=...
WATSONX_PROJECT_ID=...
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
WATSONX_EMBEDDING_MODEL_ID=ibm/slate-125m-english-rtrvr
```

If Watsonx credentials are not present, the examples use a deterministic offline backend patched into the Watsonx SDK classes. This keeps the examples runnable with only the Respan key while still exercising the Watsonx instrumentation wrappers and exported span contract.

Run one script at a time:

```bash
python 01_text_generation.py
python 02_streaming.py
python 03_chat_tool_calling.py
python 04_async_model_calls.py
python 05_embeddings.py
```

Each script prints a `custom_identifier` and `workflow_name`. The workflow name is also used as the Respan trace group identifier so the run is easy to find in traces and MCP lookups.
