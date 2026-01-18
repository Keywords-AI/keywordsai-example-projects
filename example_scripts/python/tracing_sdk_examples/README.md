# KeywordsAI Tracing SDK Examples (Python)

This directory contains comprehensive examples of how to use the `keywordsai-tracing` Python SDK.

**SDK Documentation**: https://github.com/Keywords-AI/keywordsai/blob/main/python-sdks/keywordsai-tracing/README.md

## Prerequisites

- Python 3.11 or higher
- A KeywordsAI API Key (from [keywordsai.co](https://keywordsai.co))
- (Optional) AI Provider API Keys (OpenAI, Anthropic) for real API testing

## Setup

1. Install dependencies using Poetry (from the `python` directory):
   ```bash
   cd example_scripts/python
   poetry install
   ```

2. Copy the example environment file and configure your API keys:
   ```bash
   cp tracing_sdk_examples/env.example tracing_sdk_examples/.env
   ```

3. Edit `tracing_sdk_examples/.env` with your actual API keys:
   ```env
   KEYWORDSAI_API_KEY=your_keywordsai_api_key
   KEYWORDSAI_BASE_URL=https://api.keywordsai.co/api
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Examples

### Core Functionality

| File | Description |
|------|-------------|
| `basic_usage.py` | Core decorators: `@workflow`, `@task`, `@agent`, `@tool` |

### Instrumentation & Manual Spans

| File | Description |
|------|-------------|
| `instrumentation_operations.py` | Instrumentation config, noise filtering, manual spans |

### Span Operations

| File | Description |
|------|-------------|
| `span_operations.py` | All span APIs: buffering, events, exceptions, keywordsai_params |

### Advanced Features

| File | Description |
|------|-------------|
| `multi_llm_provider.py` | Trace OpenAI + Anthropic in same workflow |
| `multi_processor.py` | Route spans to multiple processors with `add_processor()` |

## Running Examples

```bash
cd example_scripts/python

# Run with poetry
poetry run python tracing_sdk_examples/basic_usage.py
poetry run python tracing_sdk_examples/span_operations.py
poetry run python tracing_sdk_examples/multi_llm_provider.py
# ... etc
```

## Key SDK APIs

### Initialization

```python
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.instruments import Instruments

telemetry = KeywordsAITelemetry(
    app_name="my-app",
    api_key="your-api-key",
    # Optional: filter out noisy HTTP spans
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)
```

### Decorators

```python
from keywordsai_tracing.decorators import workflow, task, agent, tool

@workflow(name="my_workflow")
def my_workflow():
    pass

@task(name="my_task")
def my_task():
    pass

@agent(name="my_agent")
async def my_agent():
    pass

@tool(name="my_tool")
def my_tool():
    pass
```

### Client API

```python
from keywordsai_tracing import get_client

client = get_client()

# Update current span
client.update_current_span(
    name="new_name",
    attributes={"key": "value"},
    keywordsai_params={
        "customer_identifier": "user_123",
        "metadata": {"version": "1.0"},
    },
)

# Add events
client.add_event("event_name", {"key": "value"})

# Record exceptions
client.record_exception(exception)

# Get tracer for manual spans
tracer = client.get_tracer()
with tracer.start_as_current_span("manual_span") as span:
    span.set_attribute("key", "value")
```

### Span Buffering

```python
client = get_client()

# Buffer spans for manual processing
with client.get_span_buffer("trace-123") as buffer:
    buffer.create_span("task_1", {"result": "success"})
    buffer.create_span("task_2", {"result": "completed"})
    collected_spans = buffer.get_all_spans()

# Decide whether to process or discard
client.process_spans(collected_spans)
```

### Multi-Processor Routing

```python
from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.decorators import task

kai = KeywordsAITelemetry(...)

# Add custom processor
kai.add_processor(exporter=MyExporter(), name="debug")

# Route specific tasks to processors
@task(name="debug_task", processors="debug")
def debug_task():
    pass

@task(name="multi_task", processors=["debug", "analytics"])
def multi_task():
    pass
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `KEYWORDSAI_API_KEY` | Your KeywordsAI API key | Yes |
| `KEYWORDSAI_BASE_URL` | API base URL | No (default: https://api.keywordsai.co/api) |
| `OPENAI_API_KEY` | OpenAI API key | No (for OpenAI examples) |
| `ANTHROPIC_API_KEY` | Anthropic API key | No (for Anthropic examples) |

## Notes

- Initialize `KeywordsAITelemetry` **before** creating LLM clients for auto-instrumentation to work
- All examples include fallbacks for when API keys are not available
- Check your KeywordsAI dashboard at [keywordsai.co](https://keywordsai.co) to view traces
