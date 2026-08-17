# Microsoft Agent Framework tracing examples

These examples run Microsoft Agent Framework agents, tools, workflows, and
success/failure paths with Respan tracing enabled. The default success path
uses the real Agent Framework execution and telemetry layers with deterministic
provider responses, so its two-chat/tool tree is reproducible in CI.

The scripts load environment variables from the repo root `.env` file:

- `RESPAN_API_KEY`
- `RESPAN_BASE_URL`
- `RESPAN_GATEWAY_API_KEY`
- `RESPAN_GATEWAY_BASE_URL`
- `RESPAN_MODEL`
- `RESPAN_EXAMPLE_RUN_ID` (exact shared audit marker)
- `RESPAN_MAF_RUN_LIVE=1` (opt in to the live gateway example)

Install dependencies from this directory:

```bash
pip install -r requirements.txt
```

When testing this branch before the instrumentation package is published, also
install the local package from the Respan worktree:

```bash
pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-microsoft-agent-framework
```

Run the examples:

```bash
python 01_agent_tool_workflow.py
python 02_deterministic_failure.py
RESPAN_MAF_RUN_LIVE=1 python 03_live_agent_tool_workflow.py
```

`01_agent_tool_workflow.py` covers a native workflow, bounded Respan
workflow/task wrappers, an agent run, two LLM/chat turns, and one real
Agent Framework tool execution without a provider network dependency.
`02_deterministic_failure.py` produces an expected tool failure span without
depending on model behavior.
`03_live_agent_tool_workflow.py` is optional and uses the OpenAI-compatible
Respan gateway. It exits without creating a trace unless
`RESPAN_MAF_RUN_LIVE=1` is set.

All emitted spans use `RESPAN_EXAMPLE_RUN_ID` as both propagated metadata and
the native `trace_group_identifier`. Every script explicitly flushes and shuts
down Respan before exiting.
