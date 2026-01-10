# KeywordsAI Logging Examples

This directory contains examples for working with KeywordsAI's logging API, evaluators, and scoring functionality.

## Quick Links

- **Quickstart Guide**: https://docs.keywordsai.co/get-started/quickstart/logging
- **Evaluator Creation**: https://docs.keywordsai.co/api-endpoints/evaluate/evaluators/create
- **Log Scores Creation**: https://docs.keywordsai.co/api-endpoints/evaluate/log-scores/create

## Setup

1. **Install dependencies:**

It is recommended to use [Poetry](https://python-poetry.org/) to manage dependencies:

```bash
# From the example_scripts/python directory
poetry install
```

Alternatively, you can use pip:

```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**

Create a `.env` file in this directory (or use `.env.example` as a template):

```bash
KEYWORDSAI_API_KEY=your_keywordsai_api_key_here
KEYWORDSAI_BASE_URL=https://api.keywordsai.co/api
```

## Usage

### Run Test Create Log Score (`test_create_log_score.py`)

This script demonstrates the full workflow: creating a log, creating an evaluator, and then creating a score on that log.

```bash
poetry run python test_create_log_score.py
```

After running the test, you can view the results on the KeywordsAI platform. Navigate to the **Logs** tab on the page to see your created logs and their associated scores.

## Additional Resources

- [KeywordsAI Documentation](https://docs.keywordsai.co)
- [API Reference](https://docs.keywordsai.co/api-endpoints)
- [Integration Guides](https://docs.keywordsai.co/get-started/quickstart)
