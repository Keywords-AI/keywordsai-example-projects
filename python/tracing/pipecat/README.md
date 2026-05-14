# Pipecat Respan Examples

These examples trace Pipecat pipelines with `respan-instrumentation-pipecat`.
They load environment variables from the `respan-example-projects/.env` file.
Each script wraps the run in a Respan workflow whose name matches the script
filename, so the platform result is easy to map back to the example.

## Setup

```bash
cd python/tracing/pipecat
pip install -r requirements.txt
```

For local development against a checkout:

```bash
pip install -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-sdk \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-tracing \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/respan \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/instrumentations/respan-instrumentation-pipecat \
            -r requirements.txt
```

## Environment

The scripts read `/home/yuyang/KeywordsAI/respan-example-projects/.env`.

Required:

```bash
RESPAN_API_KEY=...
```

Optional gateway settings:

```bash
RESPAN_GATEWAY_API_KEY=...
RESPAN_GATEWAY_BASE_URL=https://api.respan.ai/api
RESPAN_MODEL=gpt-4.1-nano
```

## Examples

| Example | Description |
|---------|-------------|
| `01_offline_pipeline.py` | Local Pipecat pipeline that emits LLM frames without a provider call. |
| `02_gateway_llm_pipeline.py` | Pipecat `OpenAILLMService` routed through the Respan gateway. |

Run:

```bash
python 01_offline_pipeline.py
python 02_gateway_llm_pipeline.py
```

Each script prints a `run_id` and exports spans with
`customer_identifier=pipecat-example`, `environment=example`, workflow name, and
metadata for the script name.
