# Python Example Scripts

This directory contains example scripts demonstrating various integrations and use cases.

## Setup

### 1. Install Poetry

If you don't have Poetry installed, install it first:

```bash
# macOS/Linux/Windows (WSL)
curl -sSL https://install.python-poetry.org | python3 -

# Or using pipx
pipx install poetry
```

For more installation options, visit: https://python-poetry.org/docs/#installation

### 2. Install Dependencies

Once Poetry is installed, install the project dependencies:

```bash
poetry install
```

This will:
- Create a virtual environment automatically
- Install all required dependencies
- Install development dependencies (like `ipykernel` for Jupyter notebooks)

## Running Scripts

### Option 1: Using Poetry Run

Run any script directly with Poetry:

```bash
poetry run python gemini_sdk_example.py
poetry run python langchain_agent.py
poetry run python pirate_joke_tracing_example.py
```

### Option 2: Activate the Virtual Environment

Activate the Poetry shell and run scripts normally:

```bash
poetry shell
python gemini_sdk_example.py
python langchain_agent.py
python pirate_joke_tracing_example.py
```

To exit the Poetry shell:
```bash
exit
```

## Running Jupyter Notebooks

To run the Jupyter notebooks (like `experiment_custom_workflow.ipynb`):

```bash
poetry run jupyter notebook
# or
poetry run jupyter lab
```

Or activate the shell first:
```bash
poetry shell
jupyter notebook
```

## Available Scripts

- `gemini_sdk_example.py` - Example using Google Gemini SDK
- `langchain_agent.py` - LangChain agent implementation
- `pirate_joke_tracing_example.py` - Tracing example with KeywordsAI
- `experiment_custom_workflow.ipynb` - Jupyter notebook for custom workflows
- `logs_to_trace/` - Directory containing log-to-trace conversion utilities

## Requirements

- Python 3.11 or higher (but less than 3.14)
- Poetry for dependency management

