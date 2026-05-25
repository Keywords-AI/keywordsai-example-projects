# Pydantic AI Respan Integration Examples

These examples demonstrate how to integrate `pydantic-ai` with Respan tracing using `respan-ai` and `respan-instrumentation-pydantic-ai`.

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
>             pydantic-ai python-dotenv
> ```

2. Set your environment variables:

```bash
cp .env.example .env
```
Then edit `.env` and set your Respan API key. All examples route LLM calls through Respan, so no OpenAI key is needed.

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

## How it works

1. `Respan(...)` initializes the OpenTelemetry pipeline for Respan.
2. `PydanticAIInstrumentor()` enables Pydantic AI's native OpenTelemetry spans and normalizes them for Respan.
3. Traces, spans, and metrics from LLM calls (and tools/workflows) are sent to Respan and visible in the dashboard.
4. **Gateway pattern**: By pointing `OPENAI_BASE_URL` and `OPENAI_API_KEY` to Respan, LLM calls are routed through Respan, so only `RESPAN_API_KEY` is required.

## Further reading

- [respan-ai](https://pypi.org/project/respan-ai/)
- [respan-instrumentation-pydantic-ai](https://pypi.org/project/respan-instrumentation-pydantic-ai/)
- [Respan Documentation](https://docs.respan.ai)
- [Pydantic AI](https://ai.pydantic.dev/)
