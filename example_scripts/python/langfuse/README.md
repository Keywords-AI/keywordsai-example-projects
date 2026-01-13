# Langfuse to Keywords AI Integration

Send your Langfuse traces to Keywords AI automatically.

## Quick Start

```bash
# 1. Navigate to the Python examples directory
cd example_scripts/python

# 2. Install dependencies using Poetry
poetry install

# 3. Configure your API key in .env
cd langfuse
cp .env.example .env
# Edit .env and set your KEYWORDSAI_API_KEY

# 4. Run the example
cd ..
poetry run python langfuse/langfuse_to_keywordsai.py
```

## Installation

### Using Poetry (Recommended)

This project uses [Poetry](https://python-poetry.org/) for dependency management.

1. **Check if Poetry is installed:**
```bash
poetry --version
```

2. **Install Poetry** (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install dependencies and create virtual environment:**
```bash
cd example_scripts/python
poetry install
```

This will:
- ✅ Create a virtual environment automatically
- ✅ Install all required dependencies (`langfuse>=2.0.0`, `requests>=2.31.0`, `python-dotenv>=1.0.0`)
- ✅ Lock versions for reproducibility

**Useful Poetry commands:**
```bash
# Show virtual environment info
poetry env info

# Activate virtual environment (if needed)
poetry shell

# Update dependencies
poetry update

# Add new packages
poetry add package-name
```

### Using pip (Alternative)

```bash
pip install -r requirements.txt
```

## Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Configure your environment in `.env`:

### Required Settings
```bash
# Keywords AI API key (required)
KEYWORDSAI_API_KEY=your_api_key_here
```
Get your API key from: https://platform.keywordsai.co/

### Optional Settings

**Default Model Configuration:**
```bash
DEFAULT_MODEL=gpt-4o           # Default model for generations
DEFAULT_PROVIDER=openai        # Default provider
```

**Trace Configuration:**
```bash
TRACE_BATCH_SIZE=10           # Logs per batch (higher = fewer API calls)
TRACE_FLUSH_INTERVAL=5.0      # Seconds between flushes (lower = more real-time)
TRACE_REQUEST_TIMEOUT=10      # API request timeout in seconds
```

**Debug Configuration:**
```bash
DEBUG_MODE=true               # Enable detailed logging
PRINT_TRACES=true             # Print trace data before sending
```

**Langfuse (Optional for dual logging):**
```bash
LANGFUSE_PUBLIC_KEY=your_key
LANGFUSE_SECRET_KEY=your_key
```

## Usage

### All Spans Include Model Information

**Every span automatically includes model and provider information.** You can either:
- Use the defaults from environment variables (`DEFAULT_MODEL` and `DEFAULT_PROVIDER`)
- Specify custom models per span

```python
from langfuse_to_keywordsai import LangfuseToKeywordsAI

# Initialize
langfuse = LangfuseToKeywordsAI()

# Create a trace
trace = langfuse.trace(name="my_trace", user_id="user_123")

# Span using default model (from DEFAULT_MODEL env var)
span1 = trace.span(name="data_processing")
span1.update(
    input={"query": "Hello"},
    output={"result": "Success"}
)
span1.end()

# Span with custom model
span2 = trace.span(
    name="special_processing",
    model="gpt-3.5-turbo",
    provider_id="openai"
)
span2.update(output={"result": "Done"})
span2.end()

# End trace and send to Keywords AI
trace.end()
langfuse.flush()
```

### LLM Generations

For LLM-specific calls, use the `generation()` method:

```python
# Create LLM generation with specific model
generation = trace.generation(
    name="openai.chat",
    model="gpt-4o",           # Specify the model
    provider_id="openai"      # Specify the provider
)
generation.end(
    output=[{"role": "assistant", "content": "Response here"}]
)
```

### Supported Models & Providers

**Common models:**
- **OpenAI**: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`, `gpt-4o-mini`
- **Anthropic**: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- **Google**: `gemini-pro`, `gemini-1.5-pro`, `gemini-1.5-flash`
- **Cohere**: `command-r-plus`, `command-r`

**Provider IDs:**
- `openai`
- `anthropic`
- `google`
- `cohere`

## Run Example

### Using Poetry (Recommended)

```bash
cd example_scripts/python
poetry run python langfuse/langfuse_to_keywordsai.py
```

Poetry will automatically use the virtual environment and all installed dependencies.

### Using pip (Alternative)

```bash
python langfuse_to_keywordsai.py
```

The script includes working examples that run when executed. You should see:
- ✅ Connection confirmation
- 📊 Two complex trace examples (E-commerce order processing, AI assistant conversation)
- ✨ All spans with proper model attribution

## How It Works

1. Wraps Langfuse SDK calls
2. Captures trace/span data
3. Converts to Keywords AI format
4. Sends to Keywords AI's `/v1/traces/ingest` endpoint

## View Traces

After running, view your traces at:
https://platform.keywordsai.co/

To see your traces:
1. Navigate to the **Logs** section in the left sidebar
2. Click on the **Traces** tab (within Logs)
3. View your spans with full hierarchy, organized by trace

## Troubleshooting

**No traces appearing?**
- Check your `KEYWORDSAI_API_KEY` is correct
- Make sure you call `langfuse.flush()` before script exits
- Look for error messages in console output
- Enable debug mode: set `DEBUG_MODE=true` in `.env`

**Poetry issues?**
- **Lock file error**: Run `poetry lock --no-update` then `poetry install`
- **Wrong Python version**: Check with `poetry env info`, specify version with `poetry env use python3.10`
- **Dependencies not found**: Make sure you're in `example_scripts/python` directory when running `poetry install`
- **Module not found when running script**: Always use `poetry run python ...` or activate the shell with `poetry shell`

**Import errors?**
- Make sure you're running with Poetry: `poetry run python langfuse/langfuse_to_keywordsai.py`
- Or activate the virtual environment first: `poetry shell`

**Need help?**
- Keywords AI Docs: https://docs.keywordsai.co/
- Langfuse Docs: https://langfuse.com/docs
- Poetry Docs: https://python-poetry.org/docs/
