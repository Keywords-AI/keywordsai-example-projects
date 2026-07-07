# Pydantic AI TypeScript Respan Examples

These examples use `@respan/instrumentation-pydantic-ai` with Respan Gateway
model calls. The local repo does not currently include a documented TypeScript
Pydantic AI SDK API, so the examples emit Pydantic AI-compatible OpenTelemetry
attributes around gateway calls rather than patching a guessed SDK surface.

## Setup

```bash
cd respan-example-projects/typescript/pydantic-ai
npm install
```

Set `RESPAN_API_KEY` in `respan-example-projects/.env`. The OpenAI-compatible
gateway base URL defaults to `https://api.respan.ai/api`.

## Examples

| Script | Description |
| --- | --- |
| `01_openai_gateway.ts` | OpenAI model routed through Respan Gateway |
| `02_anthropic_gateway.ts` | Anthropic model routed through the OpenAI-compatible Gateway |
| `03_tool_span.ts` | Tool execution span plus a gateway-backed chat span |
| `04_structured_output.ts` | JSON schema response format plus local typed validation |
| `05_openinference_span.ts` | OpenInference-style Pydantic AI LLM span around a gateway call |
| `06_agent_workflow_spans.ts` | Native agent, running-tools task, tool, and chat span hierarchy |

Run one example:

```bash
npm run openai
```

Optional model overrides:

```bash
RESPAN_OPENAI_MODEL=gpt-4o-mini npm run openai
RESPAN_ANTHROPIC_MODEL=claude-sonnet-4-5 npm run anthropic
```
