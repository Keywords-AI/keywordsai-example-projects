# Strands Agents tracing examples

Runnable examples for `respan-instrumentation-strands-agents`.

## Setup

The scripts load credentials from the repository root `.env` file:

```text
respan-example-projects/.env
```

Required variable:

- `RESPAN_API_KEY`

Optional variables:

- `RESPAN_BASE_URL` defaults to `https://api.respan.ai/api`
- `RESPAN_STRANDS_MODEL` defaults to `gpt-4o-mini`

## Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python 01_basic_agent.py
python 02_tool_use.py
python 03_propagated_attributes.py
```

Each script prints a `RESPAN_EXAMPLE_RUN_ID` value. Use that value to find the
exact trace in Respan metadata or custom identifier filters. The trace workflow
name and trace group identify the example:

- `Strands Basic Example`
- `Strands Tool Use Example`
- `Strands Attribute Propagation Example`
