# LlamaIndex Respan Integration Examples

These examples show native LlamaIndex instrumentation with Respan. They route LlamaIndex OpenAI calls through the Respan gateway and load environment variables from this directory or the `respan-example-projects` repo root.

## Setup

```bash
cd python/tracing/llama-index
pip install -r requirements.txt
cp .env.example .env
```

Set `RESPAN_API_KEY` in `.env`, or use the existing `.env` file at the repo root.

For local SDK development, install the local packages first:

```bash
pip install -e /path/to/respan/python-sdks/respan \
            -e /path/to/respan/python-sdks/respan-sdk \
            -e /path/to/respan/python-sdks/respan-tracing \
            -e /path/to/respan/python-sdks/instrumentations/respan-instrumentation-llama-index \
            -r requirements.txt
```

## Examples

| Example | Description |
|---------|-------------|
| `01_hello_world.py` | Call `llama_index.llms.openai.OpenAI.complete` |
| `02_gateway_query.py` | Call `llama_index.llms.openai.OpenAI.chat` |
| `03_tracing_workflow.py` | Call `llama_index.embeddings.openai.OpenAIEmbedding.get_text_embedding` |
| `04_respan_params.py` | Build `SummaryIndex` documents and query the query engine |
| `05_tool_use_agent.py` | Run `ReActAgent` with a `FunctionTool` |

Each script sets distinct `app_name`, `example_name`, `example_run_id`, `trace_group_identifier`, and `custom_identifier` values so exported results can be traced back to the script that produced them. Set `RESPAN_EXAMPLE_RUN_ID` to apply one exact marker across a validation run. Every script shuts Respan down explicitly after its traced operation so finished spans are flushed before the process exits.

Run any example:

```bash
python 01_hello_world.py
```

## Further Reading

- [respan-instrumentation-llama-index](https://pypi.org/project/respan-instrumentation-llama-index/)
- [respan-ai](https://pypi.org/project/respan-ai/)
- [LlamaIndex](https://docs.llamaindex.ai/)
