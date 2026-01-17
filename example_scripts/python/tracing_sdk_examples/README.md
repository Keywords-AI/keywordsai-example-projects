# KeywordsAI Tracing SDK Examples (Python)

This directory contains comprehensive examples of how to use the `keywordsai-tracing` Python SDK. These examples cover all core functionalities tested in the Tracing SDK reference directory.

## Prerequisites

- Python 3.11 or higher
- A KeywordsAI API Key (from [keywordsai.com](https://keywordsai.com))
- (Optional) AI Provider API Keys (OpenAI, Anthropic) for real API testing

## Setup

1. Install dependencies using Poetry (from the `python` directory):
   ```bash
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
   
   Note: Each example script loads the `.env` file from its own directory (`tracing_sdk_examples/.env`).

## Examples

### Core Functionality

#### 1. Basic Usage (`basic_usage.py`)
Core concepts: `@workflow`, `@task`, `@agent`, `@tool` decorators.
```bash
python tracing_sdk_examples/basic_usage.py
```

#### 2. OpenAI Integration (`openai_integration.py`)
Automatic instrumentation of the OpenAI SDK.
```bash
python tracing_sdk_examples/openai_integration.py
```

#### 3. Advanced Tracing (`advanced_tracing.py`)
Agentic workflows with `@agent`, `@tool`, and custom metadata.
```bash
python tracing_sdk_examples/advanced_tracing.py
```

### Instrumentation & Configuration

#### 4. Instrumentation Management (`instrumentation_management.py`)
Different ways to configure and manage instrumentations.
```bash
python tracing_sdk_examples/instrumentation_management.py
```

#### 5. Manual Instrumentation (`manual_instrumentation.py`)
Explicit module instrumentation for environments where automatic instrumentation may not work.
```bash
python tracing_sdk_examples/manual_instrumentation.py
```

### Span Management

#### 6. Span Management (`span_management.py`)
Using the `get_client()` API to manually update spans, add events, and record exceptions.
```bash
python tracing_sdk_examples/span_management.py
```

#### 7. Update Span (`update_span.py`)
Advanced span updating with KeywordsAI-specific parameters.
```bash
python tracing_sdk_examples/update_span.py
```

#### 8. Span Buffering (`span_buffering.py`)
Manual control over span creation, buffering, and batch processing.
```bash
python tracing_sdk_examples/span_buffering.py
```

### Advanced Features

#### 9. Noise Filtering (`noise_filtering.py`)
Demonstrates how the SDK filters out auto-instrumentation noise outside of user contexts.
```bash
python tracing_sdk_examples/noise_filtering.py
```

#### 10. Multi-Provider Tracing (`multi_provider.py`)
Tracing across multiple AI providers (OpenAI + Anthropic) in a single workflow.
```bash
python tracing_sdk_examples/multi_provider.py
```

#### 11. Multi-Processor (`multi_processor.py`)
Custom span tracking with different task types, logging to files and console.
```bash
python tracing_sdk_examples/multi_processor.py
```

### Comprehensive Examples

#### 12. Usage Example (`usage_example.py`)
Comprehensive example using all utility functions: `get_client`, `update_current_span`, `add_span_event`, `record_span_exception`, `set_span_status`, and all decorators.
```bash
python tracing_sdk_examples/usage_example.py
```

#### 13. Simple OpenAI Test (`simple_openai_test.py`)
Simple test demonstrating OpenAI integration with global instance pattern.
```bash
python tracing_sdk_examples/simple_openai_test.py
```

#### 14. Test Tracing (`test_tracing.py`)
Comprehensive test with a multi-step workflow (joke creation, translation, signature generation).
```bash
python tracing_sdk_examples/test_tracing.py
```

## Key API Reference

| Feature | Description |
| --- | --- |
| `@workflow` | High-level grouping of tasks. |
| `@task` | Discrete step within a workflow. |
| `@agent` / `@tool` | Specialized for agentic patterns. |
| `get_client()` | Access manual span management methods. |
| `update_current_span()` | Update name, attributes, status, and KeywordsAI params. |
| `add_span_event()` | Add a timestamped event to the current span. |
| `record_span_exception()` | Record an error on the current span. |
| `set_span_status()` | Set span status (OK, ERROR). |
| `KeywordsAITelemetry` | Main telemetry class for initialization. |

## Decorator Parameters

### Common Parameters
- `name`: Name of the span
- `version`: Version number (optional)
- `association_properties`: Dictionary of properties to associate with the span

### Example
```python
from keywordsai_tracing.decorators import workflow, task, agent, tool

@workflow(name="my_workflow", version=1, association_properties={"user_id": "123"})
def my_workflow():
    pass

@task(name="my_task")
def my_task():
    pass

@agent(name="my_agent", association_properties={"agent_type": "assistant"})
async def my_agent():
    pass

@tool(name="my_tool")
def my_tool():
    pass
```

## Environment Variables

| Variable | Description | Required |
| --- | --- | --- |
| `KEYWORDSAI_API_KEY` | Your KeywordsAI API key | Yes |
| `KEYWORDSAI_BASE_URL` | KeywordsAI API base URL | No (default: https://api.keywordsai.co/api) |
| `OPENAI_API_KEY` | OpenAI API key | No (for OpenAI examples) |
| `ANTHROPIC_API_KEY` | Anthropic API key | No (for Anthropic examples) |

## Running All Examples

You can run all examples using the provided script pattern:

```bash
cd example_scripts/python

# Run individual examples
python tracing_sdk_examples/basic_usage.py
python tracing_sdk_examples/openai_integration.py
python tracing_sdk_examples/advanced_tracing.py
# ... etc
```

## Notes

- All examples include proper error handling and fallbacks for when API keys are not available
- Async examples use `asyncio.run()` for the main entry point
- The SDK automatically instruments OpenAI and Anthropic clients when available
- Check your KeywordsAI dashboard at [keywordsai.com](https://keywordsai.com) to view the traces
