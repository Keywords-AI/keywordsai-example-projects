# OpenAI Agents SDK tracing examples

These examples exercise `respan-instrumentation-openai-agents` against OpenAI Agents SDK `0.20.x`. The suite includes deterministic current-framework traces for success, failure, function tools, handoffs, guardrails, and streaming, plus the upstream-style live examples.

## Install

From this directory:

```bash
python -m pip install -r requirements.txt
```

For repository development, install the local packages after the registry dependencies so validation uses the current checkout:

```bash
python -m pip install -e ../../../../respan/python-sdks/respan-sdk
python -m pip install -e ../../../../respan/python-sdks/respan-tracing
python -m pip install -e ../../../../respan/python-sdks/respan
python -m pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-openai-agents
```

The suite reads the repository `.env` without overriding variables supplied by the shell. Set `RESPAN_API_KEY` and `RESPAN_BASE_URL` for trace export. Gateway-compatible live examples use that Respan credential and Chat Completions route.

The compatibility bridge disables Respan's direct OpenAI auto-instrumentation because the explicit Agents trace processor owns these provider calls; this keeps each model call to one canonical chat span even when both instrumentation packages are installed.

Hosted tools are intentionally not converted to Chat Completions. Web Search and the research bot require `RESPAN_OPENAI_AGENTS_USE_OPENAI=1` plus a direct `OPENAI_API_KEY`. File Search additionally requires `OPENAI_VECTOR_STORE_ID`. Computer Use additionally requires `RESPAN_OPENAI_AGENTS_ENABLE_COMPUTER=1` and an installed Playwright Chromium runtime:

```bash
python -m playwright install chromium
```

When those settings are absent, only the affected hosted examples are reported as explicit skips.

## Run

Run every collected example and the three legacy direct-run demos under one exact marker:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-openai-agents-check python run_all.py
```

Run only deterministic structural coverage:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-openai-agents-contract \
  python -m pytest contract_scenarios_test.py -q -s
```

Nested handoff files are directly executable without a manual `PYTHONPATH` adjustment:

```bash
python handoffs/message_filter_test.py
python handoffs/message_filter_streaming_test.py
```

Every pytest case flushes after completion, every process performs an explicit final Respan shutdown, and the same `RESPAN_EXAMPLE_RUN_ID` is attached to every emitted record.
