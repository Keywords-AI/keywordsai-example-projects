# Pydantic AI Respan Integration Examples

These examples demonstrate how to integrate `pydantic-ai` v2 with Respan tracing using `respan-ai` and `respan-instrumentation-pydantic-ai`.

## Setup

1. Install the required dependencies:

```bash
cd python/tracing/pydantic-ai
pip install -r requirements.txt
```

> **Note:** `respan-ai` and `respan-instrumentation-pydantic-ai` must be published to PyPI first. For local development, install from source instead:
> ```bash
> pip install -e /path/to/respan/python-sdks/respan \
>             -e /path/to/respan/python-sdks/instrumentations/respan-instrumentation-pydantic-ai \
>             'pydantic-ai>=2.0.0' python-dotenv
> ```

2. Use the repository root `.env` values:

```bash
RESPAN_API_KEY=...
RESPAN_BASE_URL=https://api.respan.ai/api
RESPAN_GATEWAY_BASE_URL=https://api.respan.ai/api
RESPAN_GATEWAY_API_KEY=...
PYDANTIC_AI_GATEWAY_MODEL=gemini/gemini-2.5-flash
PYDANTIC_AI_ANTHROPIC_GATEWAY_MODEL=claude-sonnet-4-5-20250929
```

The examples use Pydantic AI's real deterministic `TestModel` runtime by default so the complete native agent/chat/tool tree is repeatable. Set `RESPAN_PYDANTIC_LIVE=1` to use an explicit `OpenAIChatModel` through the configured Respan gateway. Model selection is `PYDANTIC_AI_GATEWAY_MODEL`, then `RESPAN_VERTEX_GATEWAY_MODEL`, then `RESPAN_MODEL`. The Anthropic example uses `PYDANTIC_AI_ANTHROPIC_GATEWAY_MODEL` on that opt-in live path.

## Examples

| Example | Description |
|---------|-------------|
| `01_hello_world.py` | Bare-minimum sanity check — instrument + one agent call |
| `02_gateway.py` | Gateway pattern with content capture options |
| `03_tracing.py` | Workflow/task spans with `@workflow` and `@task` decorators |
| `04_respan_params.py` | Setting `customer_identifier`, `metadata`, and `custom_tags` on spans |
| `05_tool_use.py` | Tracing a Pydantic AI agent that uses tools |
| `06_anthropic.py` | Running Anthropic models through the Respan gateway |

Run any example:

```bash
python 01_hello_world.py
```

Run the full exact-marker set:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-pydantic-ai-check python run_all.py
```

## How it works

1. `Respan(...)` initializes the OpenTelemetry pipeline for Respan.
2. `PydanticAIInstrumentor()` enables Pydantic AI's native OpenTelemetry spans and normalizes them for Respan.
3. Examples construct `OpenAIChatModel` with `OpenAIProvider(base_url=RESPAN_GATEWAY_BASE_URL, api_key=RESPAN_GATEWAY_API_KEY)`.
4. Traces, spans, and metrics from LLM calls, tools, and workflows are sent to Respan and visible in the dashboard.

## Further reading

- [respan-ai](https://pypi.org/project/respan-ai/)
- [respan-instrumentation-pydantic-ai](https://pypi.org/project/respan-instrumentation-pydantic-ai/)
- [Respan Documentation](https://docs.respan.ai)
- [Pydantic AI](https://ai.pydantic.dev/)
