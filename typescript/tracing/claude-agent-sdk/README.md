# Claude Agent SDK + Respan Examples (TypeScript)

Runnable examples showing how to trace Claude Agent SDK queries with Respan.

## Setup

```bash
cd typescript/tracing/claude-agent-sdk
npm install
cp .env.example .env
```

## Examples

```bash
npx tsx hello_world_test.ts
npx tsx wrapped_query_test.ts
npx tsx gateway_test.ts
npx tsx tool_use_test.ts
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RESPAN_API_KEY` | Yes | Your Respan API key |
| `ANTHROPIC_API_KEY` | For non-gateway examples | Your Anthropic API key |
| `RESPAN_BASE_URL` | No | Override ingest URL (default: `https://api.respan.ai/api`) |
| `RESPAN_GATEWAY_BASE_URL` | For gateway example | Gateway URL (default: `https://api.respan.ai/api`) |
