# Agno Respan Integration Examples

These examples demonstrate Agno tracing with `respan-instrumentation-agno`.
Each script wraps the Agno run in a unique Respan workflow so the result is
recognizable in the trace list.

## Setup

Install dependencies:

```bash
cd python/tracing/agno
pip install -r requirements.txt
```

Use the repository root `.env`, or create a local one:

```bash
cp .env.example .env
```

The examples route OpenAI-compatible model calls through Respan, so `RESPAN_API_KEY` is enough.

## Examples

| Example | Workflow name | Description |
|---------|---------------|-------------|
| `01_hello_world.py` | `agno_01_hello_world` | Bare-minimum Agno agent call |
| `02_gateway.py` | `agno_02_gateway` | Respan gateway routing |
| `03_tracing.py` | `agno_03_tracing_workflow` | Respan workflow and task decorators around Agno |
| `04_respan_params.py` | `agno_04_respan_params` | Customer, thread, metadata, and custom identifiers |
| `05_tool_use.py` | `agno_05_tool_use` | Agno agent with a Python tool |
| `06_team.py` | `agno_06_team` | Agno team run |

Run any example:

```bash
python 01_hello_world.py
```

## Further reading

- [respan-instrumentation-agno](https://pypi.org/project/respan-instrumentation-agno/)
- [respan-ai](https://pypi.org/project/respan-ai/)
- [Agno documentation](https://docs.agno.com/)
