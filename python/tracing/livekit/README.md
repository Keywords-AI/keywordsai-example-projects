# LiveKit Agents tracing examples

These examples exercise Respan's LiveKit Agents instrumentation with a local
mock `livekit.agents.llm.LLM` implementation plus one credential-gated LiveKit
OpenAI provider call through the configured Respan gateway. They use the real
LiveKit `LLMStream`, `ChatContext`, `CompletionUsage`, function tool, and tool
execution paths.

The examples load `RESPAN_API_KEY` and optional `RESPAN_BASE_URL` from the
`respan-example-projects` repo-root `.env`. The live provider example also honors
`RESPAN_GATEWAY_API_KEY`, `RESPAN_GATEWAY_BASE_URL`, `RESPAN_LIVEKIT_MODEL`, and
`RESPAN_MODEL`, falling back to the Respan tracing key and base URL.

Set `RESPAN_EXAMPLE_RUN_ID` to attach one exact shared marker to every emitted
record while keeping per-example custom identifiers.

## Setup

```bash
python3 -m venv .venv-livekit
. .venv-livekit/bin/activate
pip install -r python/tracing/livekit/requirements.txt
python python/tracing/livekit/run_all.py
```

## Examples

- `01_llm_chat.py` - basic `LLM.chat(...).collect()` response.
- `02_streaming_response.py` - consume the LiveKit stream directly.
- `03_tool_calling.py` - capture LLM tool-call output and execute the function tool.
- `04_context_and_error.py` - propagated Respan attributes plus an unknown-tool error span.
- `05_live_openai.py` - real LiveKit OpenAI provider stream through the Respan gateway.
