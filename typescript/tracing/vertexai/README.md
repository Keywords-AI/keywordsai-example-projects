# TypeScript Vertex AI tracing examples

These examples exercise `@respan/instrumentation-vertexai` against the
Google Vertex AI TypeScript SDK shape.

They load environment variables from the `respan-example-projects/.env` file.
By default they use real `@google-cloud/vertexai` and require
`GOOGLE_CLOUD_PROJECT` or `GOOGLE_VERTEXAI_PROJECT` plus Google Application
Default Credentials.

```bash
npm install
npm run all
```

For instrumentation smoke tests without Google credentials, fake mode must be
explicit:

```bash
VERTEXAI_EXAMPLE_MODE=fake npm run all
```

Useful environment variables:

- `RESPAN_API_KEY` or `RESPAN_GATEWAY_API_KEY`
- `RESPAN_BASE_URL` or `RESPAN_GATEWAY_BASE_URL`
- `GOOGLE_CLOUD_PROJECT` or `GOOGLE_VERTEXAI_PROJECT`
- `GOOGLE_CLOUD_LOCATION` or `GOOGLE_VERTEXAI_LOCATION`
- `VERTEXAI_MODEL`
- `VERTEXAI_EXAMPLE_MODE=fake` for deterministic fake-mode smoke tests only
- `RESPAN_EXAMPLE_RUN_ID`
