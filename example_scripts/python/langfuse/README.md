# Langfuse to KeywordsAI Integration

This example demonstrates how to use the [Langfuse Python SDK](https://python.reference.langfuse.com/) to send traces directly to KeywordsAI

## Overview

The Langfuse SDK provides a convenient API for tracing LLM applications. By simply pointing the SDK to KeywordsAI's API endpoint, you can use all of Langfuse's tracing features while sending data to KeywordsAI.

## Installation

This project uses Poetry for dependency management. Make sure you have Poetry installed:

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Navigate to the python scripts directory
cd example_scripts/python

# Install dependencies
poetry install
```

## Configuration

1. Copy `.env.example` to `.env` in the langfuse directory:
   ```bash
   cp langfuse/.env.example langfuse/.env
   ```

2. Add your KeywordsAI API key to `langfuse/.env`:
   ```env
   KEYWORDSAI_API_KEY=your_keywordsai_api_key_here
   KEYWORDSAI_BASE_URL=https://api.keywordsai.co/api
   
   # Optional: Set Langfuse credentials if you want to use actual Langfuse
   LANGFUSE_PUBLIC_KEY=
   LANGFUSE_SECRET_KEY=
   LANGFUSE_BASE_URL=
   ```
   
3. Get your API key from [KeywordsAI Platform](https://platform.keywordsai.co/platform/api/api-keys)

## Usage

### Basic Integration with Decorators

The example uses Langfuse's `@observe()` decorator for automatic tracing:

```python
import os
from langfuse import observe, get_client

# Set environment variables
os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY", "")
os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY", "")
os.environ["LANGFUSE_BASE_URL"] = os.getenv("KEYWORDSAI_BASE_URL", "")

langfuse = get_client()

# Use @observe decorator to automatically trace functions
@observe(as_type="generation")
def chat_completion(user_message: str):
    response = f"Response to: {user_message}"
    return response

# Function calls are automatically traced
result = chat_completion("Hello!")

# Flush to send data
langfuse.flush()
```

## Running the Example

```bash
# Run the example script
poetry run python langfuse/langfuse_simple_example.py
```

This will:
1. Create two example traces demonstrating different patterns
2. Example 1: Simple trace with LLM generation
3. Example 2: Deep research workflow with multi-level nested spans
4. Send all traces to KeywordsAI

## Key Features

### Automatic Tracing with Decorators
Use `@observe()` to automatically trace function calls:
```python
@observe()
def my_function(input_data):
    # Function inputs and outputs are automatically captured
    result = process_data(input_data)
    return result
```

### LLM Generations
Mark functions as generations to track LLM calls:
```python
@observe(as_type="generation")
def chat_completion(user_message: str, model: str = "gpt-4o-mini"):
    # Automatically captures input, output, and model info
    response = call_llm(user_message, model)
    return response
```

### Nested Spans
Create deep trace trees by calling decorated functions:
```python
@observe()
def parent_function():
    # This creates a parent span
    result1 = child_function_1()  # Creates child span
    result2 = child_function_2()  # Creates another child span
    return combine_results(result1, result2)

@observe()
def child_function_1():
    return "result 1"

@observe()
def child_function_2():
    return "result 2"
```

### Multi-Level Workflows
The example demonstrates a deep research workflow with:
- 4 levels of nesting
- 3 parallel branches (Wikipedia, ArXiv, Google Scholar)
- 13 total spans showing complex trace trees

## Documentation

- [Langfuse Python SDK Reference](https://python.reference.langfuse.com/)
- [Langfuse Low-Level SDK Guide](https://langfuse.com/docs/sdk/python/low-level-sdk)
- [KeywordsAI Documentation](https://docs.keywordsai.co/)

## How It Works

This integration uses a monkey-patched OpenTelemetry exporter to:
1. Intercept traces created by Langfuse's `@observe()` decorators
2. Transform OpenTelemetry span format to KeywordsAI's log format
3. Send traces to `https://api.keywordsai.co/api/v1/traces/ingest`

### Key Points
- Uses Langfuse's decorator-based API (`@observe()`)
- Automatically captures function inputs and outputs
- Creates nested span trees for complex workflows
- No need for Langfuse credentials - uses your KeywordsAI API key
- All traces appear in your KeywordsAI dashboard at https://platform.keywordsai.co/

## Expected Output

When you run the example, you'll see:
```
🚀 Initializing Langfuse with KeywordsAI base_url...

============================================================
Example 1: Simple Trace with LLM Generation
============================================================
📝 Created trace: simple-chat
🤖 Output: Response to: Hello, how are you?

============================================================
Example 2: Deep Research Workflow (Multi-Level Tree)
============================================================
🚀 Starting deep research workflow for: 'What is quantum computing?'
  📚 Gathering research from multiple sources...
   🔍 Searching Wikipedia...
      📄 Extracting info from Wikipedia...
         ✓ Validating Wikipedia...
   ...
✅ Research complete!

✅ All traces flushed!
📊 Check your KeywordsAI dashboard
```
