# Cohere TypeScript Tracing

Examples for `@respan/instrumentation-cohere`.

By default the examples use a local Cohere-compatible mock server for SDK calls and export real traces to Respan using `RESPAN_API_KEY` from the repo-root `.env`. To call Cohere directly, set `COHERE_USE_REAL_API=true` and `COHERE_API_KEY` in the same `.env` file.

```bash
npm install
npm run examples
```
