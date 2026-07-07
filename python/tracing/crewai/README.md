# CrewAI Respan Integration Examples

These examples demonstrate CrewAI tracing with `respan-instrumentation-crewai`.
They initialize Respan before importing CrewAI, route OpenAI-compatible LLM calls
through the Respan gateway, and attach stable workflow metadata so each run is
easy to find in Respan.

## Setup

Install dependencies:

```bash
cd python/tracing/crewai
pip install -r requirements.txt
```

Use the repository root `.env` file. At minimum it should include:

```bash
RESPAN_API_KEY=your-respan-api-key
RESPAN_BASE_URL=https://api.respan.ai/api
```

`RESPAN_MODEL` is optional and defaults to `gpt-4o-mini`. The examples set
`OPENAI_API_KEY` and `OPENAI_BASE_URL` from the Respan values at runtime, so a
separate provider key is not required when using the Respan gateway.

## Examples

| Example | Workflow name | Description |
| --- | --- | --- |
| `01_basic_crew.py` | `crewai_01_basic_crew` | Single-agent CrewAI task with Respan tracing |
| `02_tool_use.py` | `crewai_02_tool_use` | CrewAI agent using deterministic Python tools |
| `03_attributes.py` | `crewai_03_attributes` | CrewAI task with customer, thread, and metadata attributes |

Run one example:

```bash
python 01_basic_crew.py
```

Run the full set in isolated Python processes:

```bash
python run_all.py
```

Each script prints its workflow name and `RESPAN_EXAMPLE_RUN_ID`. Use those
values to find the corresponding spans in Respan.

## Further reading

- [respan-instrumentation-crewai](https://pypi.org/project/respan-instrumentation-crewai/)
- [respan-ai](https://pypi.org/project/respan-ai/)
- [CrewAI documentation](https://docs.crewai.com/)
