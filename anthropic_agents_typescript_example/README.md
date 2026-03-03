# Anthropic Agent SDK + Respan Examples (TypeScript)

Runnable examples showing how to trace Anthropic Agent SDK queries with Respan.

## Setup

```bash
cd anthropic_agents_typescript_example

# Install dependencies
npm install
# or: yarn install

# Copy and fill in your keys
cp .env.example .env
```

## Examples

### hello_world.ts
The simplest example — ask Claude a question, see the trace in Respan.
```bash
npx tsx hello_world.ts
```

### wrapped_query.ts
One-liner integration using `exporter.query()` — handles everything automatically.
```bash
npx tsx wrapped_query.ts
```

### gateway.ts
Route through the Respan gateway — only needs `RESPAN_API_KEY`, no Anthropic key.
```bash
npx tsx gateway.ts
```

### tool_use.ts
Run a query with tools (Read, Glob, Grep) and see tool spans in the trace.
```bash
npx tsx tool_use.ts
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RESPAN_API_KEY` | Yes | Your Respan (Keywords AI) API key |
| `ANTHROPIC_API_KEY` | For non-gateway examples | Your Anthropic API key |
| `RESPAN_BASE_URL` | No | Override ingest URL (default: `https://api.keywordsai.co/api`) |
| `RESPAN_GATEWAY_BASE_URL` | For gateway example | Gateway URL (default: `https://api.keywordsai.co/api`) |
