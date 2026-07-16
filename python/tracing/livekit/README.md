# LiveKit Agents tracing examples

These examples exercise Respan's LiveKit Agents instrumentation with a local
mock `livekit.agents.llm.LLM` implementation. They use the real LiveKit
`LLMStream`, `ChatContext`, `CompletionUsage`, function tool, and tool execution
paths while avoiding provider or LiveKit Cloud credentials.

The examples load `RESPAN_API_KEY` and optional `RESPAN_BASE_URL` from the
`respan-example-projects` repo-root `.env`.

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
