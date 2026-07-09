# Python Direct LLM Auto-Instrumentation

This example verifies `Respan()` auto-activates only the gateway-compatible LLM SDKs that can make real Respan gateway calls with `RESPAN_API_KEY`.

The runner prints the full Python auto-instrumentation registry. SDKs that require provider credentials, local runtimes, or OpenAI-compatible gateway transport through another SDK are shown as manual-only to avoid surprising skips and duplicate spans.

## Run

From `respan-example-projects`:

```bash
.venv/bin/python -m pip install -r python/tracing/auto-instrument-direct-llm/requirements.txt
.venv/bin/python python/tracing/auto-instrument-direct-llm/01_batch_auto_instrument.py
```

Run one default-auto case:

```bash
.venv/bin/python python/tracing/auto-instrument-direct-llm/01_batch_auto_instrument.py --only mistralai
```

The runner automatically prefers a sibling local `respan` checkout. Set `RESPAN_REPO=/path/to/respan` to override that path.

## Default-Auto Coverage

| Case | SDK package exercised | Gateway behavior |
| --- | --- | --- |
| `openai` | `openai` | Real chat completion through `https://api.respan.ai/api`. |
| `anthropic` | `anthropic` | Real Messages API call through `https://api.respan.ai/api/anthropic`. |
| `google-genai` | `google-genai` | Real Gemini call through `https://api.respan.ai/api/google/gemini`. |
| `together` | `together` | Real chat completion through the Respan gateway. |
| `mistralai` | `mistralai` | Real Mistral SDK call through the Respan gateway using a `mistral/...` model ID. |
| `litellm` | `litellm` | Real LiteLLM completion through the Respan gateway; nested OpenAI SDK spans are suppressed to avoid duplicates. |

## Manual-Only Cases

These instrumentations remain available for explicit `instrumentations=[...]`, but they are not activated by `Respan()` default auto mode:

| Case | Reason |
| --- | --- |
| `cohere`, `groq` | Their gateway models are reachable through OpenAI-compatible transport, so OpenAI instrumentation covers normal `RESPAN_API_KEY` gateway calls. Native SDK base URLs are not currently verified; current live checks return endpoint 404s. |
| `aws-bedrock`, `replicate`, `sagemaker`, `portkey`, `openrouter` | Respan gateway usage is OpenAI-compatible, so OpenAI instrumentation covers normal `RESPAN_API_KEY` gateway calls. Native SDK instrumentation is for direct provider credentials. |
| `vertexai`, `ollama`, `aleph-alpha`, `huggingface`, `watsonx`, `writer` | Native SDK usage requires provider/cloud credentials, a local runtime, or a local/downloadable model. |

## Environment

The example loads `respan-example-projects/.env`.

Required:

- `RESPAN_API_KEY`

Common optional values:

- `RESPAN_BASE_URL`
- `RESPAN_GATEWAY_API_KEY`
- `RESPAN_GATEWAY_BASE_URL`
- `RESPAN_MODEL`
- `RESPAN_ANTHROPIC_MODEL`
- `RESPAN_GOOGLE_GENAI_MODEL`
- `RESPAN_TOGETHER_MODEL`
- `RESPAN_MISTRAL_MODEL`
- `RESPAN_EXAMPLE_RUN_ID`

## What This Checks

- `Respan()` initializes with no explicit instrumentor list.
- Default auto mode activates only verified real gateway SDKs.
- Manual-only direct SDKs appear in registry status with reasons.
- SDK clients are imported and created after tracing initialization.
- The printed `trace_group_identifier` can be used to find the run in the platform.
