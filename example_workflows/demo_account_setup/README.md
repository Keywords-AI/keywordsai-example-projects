# KeywordsAI Logging Examples

This directory contains examples for working with KeywordsAI's logging API, evaluators, and scoring functionality.

## Quick Links

- **Quickstart Guide**: https://docs.keywordsai.co/get-started/quickstart/logging
- **Create a Prompt**: https://docs.keywordsai.co/get-started/quickstart/create-a-prompt
- **Evaluator Creation**: https://docs.keywordsai.co/api-endpoints/evaluate/evaluators/create
- **Log Scores Creation**: https://docs.keywordsai.co/api-endpoints/evaluate/log-scores/create

## Setup

1. **Install dependencies:**

It is recommended to use [Poetry](https://python-poetry.org/) to manage dependencies:

```bash
# From the example_workflows directory
cd /home/yuyang/KeywordsAI/keywordsai-example-projects/example_workflows
poetry install
```

Alternatively, you can use pip:

```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**

Copy the `.env.example` file to `.env` and update it with your API credentials:

```bash
cp .env.example .env
```

Then edit `.env` and set your API key:

```bash
KEYWORDSAI_API_KEY=your_keywordsai_api_key_here
KEYWORDSAI_BASE_URL=https://api.keywordsai.co/api
```

You can also customize other settings in `.env` such as:
- Model names (DEFAULT_MODEL, DEFAULT_MODEL_MINI, DEFAULT_MODEL_CLAUDE)
- Evaluator settings (EVALUATOR_LLM_ENGINE, EVALUATOR_TEMPERATURE, EVALUATOR_MAX_TOKENS)
- Score ranges (DEFAULT_MIN_SCORE, DEFAULT_MAX_SCORE, DEFAULT_PASSING_SCORE)
- Prompt settings (PROMPT_TEMPERATURE, PROMPT_MAX_TOKENS)

## Usage

All scripts should be run from the `example_workflows` directory using Poetry:

```bash
cd /home/yuyang/KeywordsAI/keywordsai-example-projects/example_workflows
```

### 1. Basic Logging (`basic_logging.py`)

This script demonstrates basic logging functionality with various examples:
- Simple log entry
- Log with custom identifier
- Log with span name
- Multi-turn conversation log

```bash
poetry run python demo_account_setup/basic_logging.py
```

### 2. Create Evaluator (`create_evaluator.py`)

This script demonstrates how to create custom evaluators in KeywordsAI:
- LLM evaluator for response quality (numerical)
- Helpfulness evaluator (categorical)
- Factual accuracy evaluator (boolean)
- Overall satisfaction evaluator (1-5 scale)

```bash
poetry run python demo_account_setup/create_evaluator.py
```

### 3. Create Log Scores (`create_log_scores.py`)

This script provides examples and documentation for creating scores on logs using evaluators. It includes:
- Single score creation
- Score with metadata
- Batch score creation
- Complete workflow examples

**Note:** This script primarily shows example code patterns. For actual execution, see `test_create_log_score.py`.

```bash
poetry run python demo_account_setup/create_log_scores.py
```

### 4. Test Create Log Score (`test_create_log_score.py`)

This script demonstrates the complete end-to-end workflow:
1. Creates a log entry
2. Creates an evaluator
3. Creates a score on the log using the evaluator

```bash
poetry run python demo_account_setup/test_create_log_score.py
```

### 5. Create Prompt (`create_prompt.py`)

This script demonstrates how to create and manage prompts in KeywordsAI:
- Create a new prompt
- Create prompt versions with messages
- List all prompts
- Get a specific prompt
- List prompt versions
- Get a specific prompt version

Prompts are reusable templates for LLM conversations that can be versioned and deployed.

```bash
poetry run python demo_account_setup/create_prompt.py
```

After running any of these scripts, you can view the results on the KeywordsAI platform:
- Navigate to the **Logs** tab to see your created logs and their associated scores
- Navigate to the **Prompt Management** section to see your created prompts

## Additional Resources

- [KeywordsAI Documentation](https://docs.keywordsai.co)
- [API Reference](https://docs.keywordsai.co/api-endpoints)
- [Integration Guides](https://docs.keywordsai.co/get-started/quickstart)
