# Guardrails AI Tracing Examples

These examples show how to trace Guardrails AI validation with Respan.

## Setup

From the repository root:

```bash
python -m venv .venv-guardrails
source .venv-guardrails/bin/activate
pip install -r python/tracing/guardrails/requirements.txt
```

The requirements file installs `guardrails-ai` from the Guardrails GitHub
`v0.9.3` tag because the PyPI project is currently quarantined and hidden from
installer clients. It also pins `guardrails-api==0.3.3`, matching the upstream
issue workaround.

The scripts load `RESPAN_API_KEY`, `RESPAN_BASE_URL`, and optional `RESPAN_MODEL`
from the repo-root `.env` file. OpenAI-compatible calls are routed through the
Respan gateway with `RESPAN_API_KEY`.

## Run

```bash
python python/tracing/guardrails/01_pydantic_parse.py
python python/tracing/guardrails/02_gateway_structured_generation.py
python python/tracing/guardrails/03_propagated_attributes.py
```

`01_pydantic_parse.py` and `03_propagated_attributes.py` validate known output.
`02_gateway_structured_generation.py` calls the configured gateway model.

The examples emit workflow spans with stable names:

| Script | Workflow name |
|--------|---------------|
| `01_pydantic_parse.py` | `guardrails_pydantic_parse_workflow` |
| `02_gateway_structured_generation.py` | `guardrails_gateway_structured_generation_workflow` |
| `03_propagated_attributes.py` | `guardrails_propagated_attributes_workflow` |
