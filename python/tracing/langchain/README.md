# LangChain Respan Tracing Examples

These numbered scripts demonstrate LangChain callback surfaces that
`respan-instrumentation-langchain` exports through Respan tracing. Each numbered
file focuses on one LangChain function or behavior.

Most scripts use LangChain fake models, so they run without model-provider API
keys. `13_model_with_structured_output.py` and
`23_agent_structured_output.py` use a provider-backed chat model because
structured output is provider/model dependent.

## Setup

```bash
cd /home/yuyang/KeywordsAI/respan-example-projects/python/tracing/langchain
pip install -r requirements.txt

# For local SDK development:
pip install -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-tracing \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/instrumentations/respan-instrumentation-langchain
```

Optional tracing export:

```bash
export RESPAN_API_KEY=your_respan_api_key
export RESPAN_BASE_URL=https://api.respan.ai/api
```

Provider-backed structured output examples also need:

```bash
export OPENAI_API_KEY=your_openai_api_key
# Optional OpenAI-compatible proxy:
export OPENAI_BASE_URL=https://your-openai-compatible-base-url
```

Run one example:

```bash
python 00_quickstart.py
```

Run the complete bounded set with `python run_all_examples.py`.

## Examples

| Script | LangChain function or behavior |
| --- | --- |
| `00_quickstart.py` | Hello-world Respan LangChain instrumentation quickstart |
| `01_chat_model_invoke.py` | Chat model `invoke()` |
| `02_chat_model_stream.py` | Chat model `stream()` |
| `03_chat_model_batch.py` | Chat model `batch()` |
| `04_chat_model_batch_as_completed.py` | Chat model `batch_as_completed()` |
| `05_chat_model_ainvoke.py` | Chat model `ainvoke()` |
| `06_chat_model_astream.py` | Chat model `astream()` |
| `07_chat_model_abatch.py` | Chat model `abatch()` |
| `08_chat_model_abatch_as_completed.py` | Chat model `abatch_as_completed()` |
| `09_chat_model_astream_events.py` | Chat model `astream_events()` |
| `10_llm_invoke.py` | Legacy string LLM `invoke()` |
| `11_llm_stream.py` | Legacy string LLM `stream()` |
| `12_model_bind_tools.py` | Model `bind_tools()` and tool-call execution |
| `13_model_with_structured_output.py` | Model `with_structured_output()` |
| `14_tool_invoke.py` | Tool `invoke()` |
| `15_tool_ainvoke.py` | Tool `ainvoke()` |
| `16_prompt_chain_invoke.py` | Prompt/model/parser chain `invoke()` |
| `17_runnable_parallel_invoke.py` | `RunnableParallel.invoke()` |
| `18_retriever_invoke.py` | Retriever `invoke()` |
| `19_agent_invoke.py` | Agent `invoke()` |
| `20_agent_stream_updates.py` | Agent `stream(..., stream_mode="updates")` |
| `21_agent_stream_messages.py` | Agent `stream(..., stream_mode="messages")` |
| `22_agent_stream_custom.py` | Agent `stream(..., stream_mode="custom")` |
| `23_agent_structured_output.py` | Agent `response_format` structured output |
| `24_custom_event.py` | `dispatch_custom_event()` |
| `25_runnable_with_retry.py` | Runnable `with_retry()` |
| `26_chain_error.py` | Chain error callback |
| `27_tool_error.py` | Tool error callback |
| `28_retriever_error.py` | Retriever error callback |

## Coverage Notes

The set is based on current LangChain Python docs and the current
`respan-instrumentation-langchain` callback handler. It covers the documented
model invocation methods (`invoke`, `stream`, batch variants, async variants,
events), tool calling, structured output, tools, retrievers, agents, streaming
modes, custom events, retries, and error callbacks. It does not enumerate every
provider integration or every helper method inherited by `Runnable`, because
those map to the same callback types above.

Official docs checked:

- https://docs.langchain.com/oss/python/langchain/models
- https://docs.langchain.com/oss/python/langchain/tools
- https://docs.langchain.com/oss/python/langchain/agents
- https://docs.langchain.com/oss/python/langchain/streaming
- https://docs.langchain.com/oss/python/langchain/structured-output
- https://docs.langchain.com/oss/python/langchain/retrieval
- https://reference.langchain.com/python/langchain-core/callbacks/manager/dispatch_custom_event
