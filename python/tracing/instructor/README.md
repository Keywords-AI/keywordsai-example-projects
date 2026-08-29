# Instructor Respan Integration Examples

These examples exercise Instructor's own client functions while routing traffic
through the Respan gateway. Tracing is initialized with `respan`, and
Instructor-specific spans come from `respan-instrumentation-instructor`.

## Setup

Install the required dependencies:

```bash
cd python/tracing/instructor
pip install -r requirements.txt
```

Use the `.env` file in the `respan-example-projects` repo root, or export the
same variables in your shell:

```bash
export RESPAN_API_KEY="your-respan-api-key"
export RESPAN_BASE_URL="https://api.respan.ai/api"
```

The scripts call `load_dotenv(find_dotenv(), override=True)`, so running them
from `python/tracing/instructor` still picks up the repo-root `.env`. All
examples route OpenAI-compatible traffic through the Respan gateway, so no
separate OpenAI key is required.

Each script wraps its Instructor call in a uniquely named Respan workflow and
propagates `example_script` metadata, so traces are easy to filter alongside
the Instructor chat span. `RESPAN_EXAMPLE_RUN_ID` is propagated to every span,
and every script shuts down Respan in `finally`.

By default the examples use `gpt-4o-mini`. Override it with:

```bash
export INSTRUCTOR_MODEL="gpt-4o-mini"
```

## Examples

| Example | Instructor API exercised |
|---------|--------------------------|
| `01_create.py` | `client.create(...)` with a typed response model |
| `02_validation_hooks.py` | `max_retries`, Instructor hooks, and Respan propagated attributes |
| `03_create_with_completion.py` | `client.create_with_completion(...)` for parsed output plus raw completion |
| `04_create_iterable.py` | `client.create_iterable(...)` for streaming multiple complete objects |
| `05_async_create.py` | async `client.create(...)` |

Run any example:

```bash
python 01_create.py
```

Run the complete maintained set:

```bash
python run_all.py
```

## Further Reading

- [Instructor](https://python.useinstructor.com/)
- [respan-instrumentation-instructor](https://pypi.org/project/respan-instrumentation-instructor/)
- [Respan Documentation](https://docs.respan.ai)
