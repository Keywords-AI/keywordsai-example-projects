# Flue TypeScript tracing examples

These examples exercise `@respan/instrumentation-flue` against Flue's stable
runtime event contract.

They use the `respan-example-projects/.env` file at the repo root. Required:

- `RESPAN_API_KEY`

Optional:

- `RESPAN_BASE_URL`
- `RESPAN_EXAMPLE_RUN_ID`
- `RESPAN_EXAMPLE_DEBUG=true`

Run everything:

```bash
npm install
RESPAN_EXAMPLE_RUN_ID=flue-ts-local npm run examples
```

The examples are deterministic and do not call an LLM provider. They create
Flue runtime contexts and emit representative workflow, agent, model-turn,
tool, task, compaction, log, and recovery events through Flue's `observe()`
path so the Respan instrumentor sees the same event shapes a running Flue app
emits.
