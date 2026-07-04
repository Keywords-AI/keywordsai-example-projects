# Microsoft Agent Framework tracing examples

These examples run Microsoft Agent Framework agents, tools, workflows, and a
deterministic failure path with Respan tracing enabled.

The scripts load environment variables from the repo root `.env` file:

- `RESPAN_API_KEY`
- `RESPAN_BASE_URL`
- `RESPAN_GATEWAY_API_KEY`
- `RESPAN_GATEWAY_BASE_URL`
- `RESPAN_MODEL`

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
```

`01_agent_tool_workflow.py` covers a workflow run, an agent run, the LLM/chat
path through the OpenAI-compatible Respan gateway, and a tool call.
`02_deterministic_failure.py` produces an expected tool failure span without
depending on model behavior.
