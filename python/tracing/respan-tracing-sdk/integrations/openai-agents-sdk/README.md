# OpenAI Agents SDK + Respan Tracing SDK

This directory contains examples of tracing OpenAI Agents SDK applications using the `respan-tracing` SDK.

## Approach: `respan-tracing` vs `respan-exporter-openai-agents`

These examples use `respan-tracing` (the general-purpose tracing SDK) instead of `respan-exporter-openai-agents` (the dedicated exporter). The key differences:

| Feature | `respan-tracing` | `respan-exporter-openai-agents` |
|---------|-------------------|----------------------------------|
| Auto-instruments OpenAI calls | Yes (via OpenTelemetry) | No (uses Agents SDK trace processor) |
| Decorator-based hierarchy | `@workflow`, `@task`, `@agent`, `@tool` | Uses Agents SDK `trace()` context |
| Span updates & metadata | `get_client().update_current_span()` | Limited to trace processor |
| Works with any LLM provider | Yes | OpenAI Agents SDK only |

**When to use `respan-tracing`**: You want decorator-based tracing hierarchy, auto-instrumentation of all OpenAI SDK calls, and the ability to add custom span attributes and metadata.

## Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

3. Run any example:
   ```bash
   python basic/hello_world.py
   python tools/function_tools.py
   python handoffs/basic_handoff.py
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `RESPAN_API_KEY` | Your Respan API key | Yes |
| `RESPAN_BASE_URL` | API base URL (default: `https://api.respan.ai/api`) | No |
| `OPENAI_API_KEY` | OpenAI API key for agent LLM calls | Yes |

## Examples

### Basic

| File | Description |
|------|-------------|
| `basic/hello_world.py` | Simple agent with `@workflow` wrapper |
| `basic/streaming.py` | Streaming responses with event tracing |

### Tools

| File | Description |
|------|-------------|
| `tools/function_tools.py` | `@function_tool` wrapped with respan `@tool` decorator |
| `tools/web_search.py` | WebSearchTool traced as a workflow |
| `tools/mcp_server.py` | MCP stdio server integration with `@task` |

### Handoffs

| File | Description |
|------|-------------|
| `handoffs/basic_handoff.py` | Triage agent routing to specialized agents |
| `handoffs/handoff_with_context.py` | Handoff with input_filter and metadata |

### Guardrails

| File | Description |
|------|-------------|
| `guardrails/input_guardrails.py` | Input guardrail with tripwire detection |
| `guardrails/output_guardrails.py` | Output guardrail for sensitive data |
| `guardrails/tool_guardrails.py` | Tool input/output guardrails |

### Human in the Loop

| File | Description |
|------|-------------|
| `human_in_the_loop/approval_flow.py` | Tool approval with span events |

### Sessions

| File | Description |
|------|-------------|
| `sessions/persistent_memory.py` | Multi-turn conversation with session metadata |

### Agent Patterns

| File | Description |
|------|-------------|
| `agent_patterns/agents_as_tools.py` | Agent.as_tool() with orchestrator pattern |
| `agent_patterns/parallelization.py` | Concurrent agent execution with parallel `@task` |
| `agent_patterns/deterministic_flow.py` | Sequential pipeline with validation gates |

## Tracing Pattern

Every example follows this pattern:

```python
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow, task
from respan_tracing.instruments import Instruments
from agents import Agent, Runner

# 1. Initialize telemetry BEFORE creating agents/clients
telemetry = RespanTelemetry(
    app_name="my-app",
    api_key=os.getenv("RESPAN_API_KEY"),
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

# 2. Define agents
agent = Agent(name="Assistant", instructions="...")

# 3. Wrap operations with decorators
@workflow(name="my_workflow")
async def run():
    result = await Runner.run(agent, "prompt")
    return result.final_output

# 4. Run the workflow
await run()
```

Auto-instrumentation captures all LLM calls made by the agents. Decorators add structured hierarchy (workflow > task > auto-instrumented LLM spans).
