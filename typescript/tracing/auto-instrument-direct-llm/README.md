# TypeScript Direct LLM Auto-Instrumentation

This example verifies the `@respan/respan` facade auto-discovers direct LLM SDK instrumentations without explicit instrumentor imports. It also prints the full known auto-instrumentation registry so framework, agent, tooling, and observability packages added on main are visible as disabled-by-default instead of silently ignored.

Direct LLM SDKs auto-enabled by this example:

- OpenAI SDK
- Anthropic SDK
- Azure OpenAI clients from `openai`
- Google Vertex AI SDK
- OpenRouter SDK

Framework and agent packages are intentionally not auto-enabled to avoid duplicate LLM spans. Add those instrumentors explicitly when the application is tracing a framework-level workflow.

## Run

```bash
npm install
npm run batch
```

The batch runner always reports all supported direct LLM SDKs. It runs configured providers and marks unavailable providers as skipped. OpenAI, Anthropic, Azure OpenAI, and OpenRouter route through the Respan gateway by default, so the repository root `.env` only needs a Respan key for those cases.

The original single-provider check is still available:

```bash
npm run openai-gateway
```

## Gateway Coverage

| Case | SDK package exercised | Gateway wiring | Default behavior |
| --- | --- | --- | --- |
| `openai` | `openai` | `baseURL=https://api.respan.ai/api` | Runs with `RESPAN_MODEL` or `gpt-4o` |
| `anthropic` | `@anthropic-ai/sdk` | `baseURL=https://api.respan.ai/api/anthropic` | Runs with `RESPAN_ANTHROPIC_MODEL` or Claude Sonnet |
| `azure-openai` | `openai` `AzureOpenAI` client | Documented Respan gateway subclass that skips Azure deployment path rewriting | Runs with `RESPAN_AZURE_GATEWAY_MODEL` or `azure/gpt-5.5` |
| `openrouter` | `@openrouter/sdk` | `serverURL=https://api.respan.ai/api` | Runs with `RESPAN_OPENROUTER_GATEWAY_MODEL` or `RESPAN_MODEL` |
| `vertexai` | `@google-cloud/vertexai` | Native SDK does not expose an OpenAI-compatible gateway path | Runs only when Google Cloud Vertex env is configured |
| `vertexai-gateway-openai-compatible` | `openai` | OpenAI-compatible gateway route for a Vertex provider slug | Runs only when `RESPAN_VERTEX_GATEWAY_MODEL` is set |

The Vertex AI gateway route is intentionally separated from the native Vertex AI SDK case. Respan gateway Vertex routing uses OpenAI-compatible chat completions, while the direct auto-instrumentation package patches `@google-cloud/vertexai`.

## Environment

The example loads `respan-example-projects/.env`.

Required:

- `RESPAN_API_KEY`

Common optional values:

- `RESPAN_BASE_URL`
- `RESPAN_GATEWAY_API_KEY`
- `RESPAN_GATEWAY_BASE_URL`
- `RESPAN_MODEL`
- `RESPAN_ANTHROPIC_MODEL`
- `RESPAN_AZURE_GATEWAY_MODEL`
- `RESPAN_OPENROUTER_GATEWAY_MODEL`
- `RESPAN_VERTEX_GATEWAY_MODEL`
- `RESPAN_EXAMPLE_RUN_ID`

Provider-specific optional values for extra native SDK cases:

- Vertex AI native SDK: `GOOGLE_CLOUD_PROJECT` or `VERTEXAI_PROJECT`, plus `GOOGLE_CLOUD_LOCATION` or `VERTEXAI_LOCATION`, optional `VERTEXAI_MODEL`

Provider-prefixed gateway model notes:

- Azure OpenAI defaults to `azure/gpt-5.5` because that route works with the current shared gateway key.
- OpenRouter defaults to `RESPAN_MODEL` so the native OpenRouter SDK can run through the gateway without a separate OpenRouter provider key. Set `RESPAN_OPENROUTER_GATEWAY_MODEL=openrouter/...` after configuring OpenRouter credentials in Respan.
- Vertex gateway routing is opt-in because the current shared key/provider route can fail at provider connection time. Set `RESPAN_VERTEX_GATEWAY_MODEL=vertex_ai/...` when the provider route is ready.

## What This Checks

- `new Respan()` is initialized with no `instrumentations` option.
- Direct LLM instrumentors are auto-discovered and activated when installed.
- Non-direct packages from the enriched TypeScript instrumentation list are reported as disabled-by-default with reasons.
- SDK clients are imported and created after tracing initialization.
- OpenAI, Anthropic, Azure OpenAI, and OpenRouter calls are routed through the Respan gateway.
- Each configured SDK call runs in its own workflow with shared batch metadata.
