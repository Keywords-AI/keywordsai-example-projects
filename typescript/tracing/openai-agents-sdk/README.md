# OpenAI Agents SDK Semantic Tracing

Runs a TypeScript version of the Python OpenAI Agents complex edge-case example through the Respan gateway and exports spans through the patched `@respan/tracing` semantic span-name path.

```bash
npm install
npm run complex
```

The script reads `RESPAN_API_KEY`, `RESPAN_BASE_URL`, and optional `RESPAN_MODEL` from the repo root `.env`. It does not require `OPENAI_API_KEY`.
