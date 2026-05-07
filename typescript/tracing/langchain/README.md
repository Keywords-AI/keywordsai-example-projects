# LangChain Respan Tracing TypeScript Examples

These numbered scripts demonstrate the LangChain JS callback surfaces exported
by `@respan/instrumentation-langchain`.

Most scripts use LangChain fake models, so they run without model-provider API
keys. Set `RESPAN_API_KEY` to export spans to Respan.

## Setup

```bash
cd /home/yuyang/KeywordsAI/respan-example-projects/typescript/tracing/langchain
npm install

# For local SDK development, build the local instrumentation package first:
yarn -C /home/yuyang/KeywordsAI/respan/javascript-sdks workspace @respan/instrumentation-langchain build
```

Optional tracing export:

```bash
export RESPAN_API_KEY=your_respan_api_key
export RESPAN_BASE_URL=https://api.respan.ai/api
```

Run one example:

```bash
npm run 00
```

Run all examples:

```bash
npm run run:all
```

## Examples

| Script | LangChain JS function or behavior |
| --- | --- |
| `00_quickstart.ts` | Hello-world Respan LangChain instrumentation quickstart |
| `01_chat_model_invoke.ts` | Chat model `invoke()` |
| `02_chat_model_stream.ts` | Chat model `stream()` |
| `03_chat_model_batch.ts` | Chat model `batch()` |
| `04_chat_model_stream_events.ts` | Runnable `streamEvents()` |
| `05_chat_model_stream_log.ts` | Runnable `streamLog()` |
| `06_llm_invoke.ts` | Legacy string LLM `invoke()` |
| `07_llm_stream.ts` | Legacy string LLM `stream()` |
| `08_model_bind_tools.ts` | Model `bindTools()` |
| `09_model_with_structured_output.ts` | Model `withStructuredOutput()` |
| `10_tool_invoke.ts` | Tool `invoke()` |
| `11_tool_batch.ts` | Tool `batch()` |
| `12_prompt_chain_invoke.ts` | Prompt/model/parser chain `invoke()` |
| `13_runnable_sequence_pipe.ts` | Runnable `pipe()` / `RunnableSequence` |
| `14_runnable_parallel_invoke.ts` | `RunnableParallel.invoke()` |
| `15_runnable_assign_pick.ts` | Runnable `assign()` and `pick()` |
| `16_retriever_invoke.ts` | Retriever `invoke()` |
| `17_agent_invoke.ts` | Agent `invoke()` |
| `18_agent_stream_updates.ts` | Agent `stream(..., { streamMode: "updates" })` |
| `19_agent_stream_messages.ts` | Agent `stream(..., { streamMode: "messages" })` |
| `20_agent_stream_custom.ts` | Agent `stream(..., { streamMode: "custom" })` |
| `21_agent_structured_output.ts` | Agent `responseFormat` structured output |
| `22_custom_event.ts` | `dispatchCustomEvent()` with `streamEvents()` |
| `23_runnable_with_retry.ts` | Runnable `withRetry()` |
| `24_runnable_with_fallbacks.ts` | Runnable `withFallbacks()` |
| `25_chain_error.ts` | Chain error callback |
| `26_llm_error.ts` | LLM error callback |
| `27_tool_error.ts` | Tool error callback |
| `28_retriever_error.ts` | Retriever error callback |
| `29_langgraph_invoke.ts` | LangGraph `invoke()` |
| `30_langgraph_stream_updates.ts` | LangGraph `stream(..., { streamMode: "updates" })` |
| `31_langflow_component_grouping.ts` | Langflow-style component callback grouping |

## Coverage Notes

The set follows the current LangChain JS docs and reference pages for models,
tools, agents, streaming, runnables, retrievers, custom events, LangGraph, and
structured output. It focuses on callback-producing surfaces that
`@respan/instrumentation-langchain` handles: chains/workflows, chat models, text
LLMs, tools, retrievers, agents, custom events, retries, fallbacks, errors,
LangGraph runs, and Langflow-style grouped root runs.

Official docs checked:

- https://docs.langchain.com/oss/javascript/langchain/models
- https://docs.langchain.com/oss/javascript/langchain/tools
- https://docs.langchain.com/oss/javascript/langchain/agents
- https://docs.langchain.com/oss/javascript/langchain/streaming/overview
- https://docs.langchain.com/oss/javascript/langgraph/streaming
- https://reference.langchain.com/javascript/langchain-core/runnables/RunnableSequence
- https://reference.langchain.com/javascript/langchain-core/runnables/RunnableParallel
- https://reference.langchain.com/javascript/langchain-core/retrievers/BaseRetriever
- https://reference.langchain.com/javascript/langchain/index/createAgent
