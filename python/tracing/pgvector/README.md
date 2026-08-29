# PGVector Tracing Examples

These examples validate Respan's PGVector instrumentation around current
`pgvector` and psycopg 3 sync/async operations. The first three workflows use a
deterministic process-local psycopg loopback, so they require no database and
still exercise the real instrumentation patch/export path. The optional fourth
workflow connects to PostgreSQL when `PGVECTOR_DSN` is configured. That live
workflow covers psycopg 3 sync and async connections, named server cursors,
explicit async cursor teardown, and pgvector's psycopg 2 registration adapter.

The deterministic workflows cover:

- sync and async vector registration, execute, and fetch operations
- connection, cursor, and server-cursor wrappers without duplicate spans
- distance operators, bulk parameters, vector-result previews, and rollback
- one caught database failure that exports a failed child operation
- bounded/redacted connection serialization despite a deliberately unsafe repr

## Setup

The repository-root `.env` must contain `RESPAN_API_KEY`. To run the optional
live workflow, add a PostgreSQL DSN for a database where the `vector` extension
is already installed:

```dotenv
PGVECTOR_DSN=postgresql://user:password@localhost/database
```

Install the example dependencies and link the local instrumentation while it is
under development:

```bash
cd python/tracing/pgvector
pip install -r requirements.txt
pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-pgvector
python run_all.py
```

Set `RESPAN_EXAMPLE_RUN_ID` to place every emitted workflow under one exact
audit marker. `run_all.py` propagates that marker to each child process and
applies a 60-second per-script timeout; override it with
`RESPAN_EXAMPLE_TIMEOUT_SECONDS`. Every workflow closes cursors/connections and
explicitly flushes and shuts down Respan.
