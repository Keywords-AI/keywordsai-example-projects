# Claude Agent SDK - Gateway (TypeScript)

Route Claude Agent SDK calls through the Respan gateway. Only needs `RESPAN_API_KEY`; no Anthropic key is required.

## Setup

```bash
cd typescript/gateway/claude-agent-sdk
npm install
```

Create a `.env` file:

```
RESPAN_API_KEY=your_key
```

## Examples

| Script | Description |
|--------|-------------|
| `basic_gateway.ts` | Basic gateway call with one key for LLM + tracing |
| `tool_use_gateway.ts` | Tool use (Read, Glob, Grep) routed through gateway |

```bash
npx tsx basic_gateway.ts
npx tsx tool_use_gateway.ts
```

## Docs

- [Gateway > Claude Agent SDK](https://www.respan.ai/docs/integrations/gateway/claude-agent-sdk)
- [Tracing > Claude Agent SDK](https://www.respan.ai/docs/integrations/tracing/claude-agent-sdk)
