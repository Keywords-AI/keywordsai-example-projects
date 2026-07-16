# OpenAI Agents SDK TypeScript

Gateway-first examples for `@openai/agents@0.12.x` with `@respan/instrumentation-openai-agents`.

Set `RESPAN_API_KEY` in `respan-example-projects/.env`. Optional overrides: `RESPAN_GATEWAY_API_KEY`, `RESPAN_GATEWAY_BASE_URL`, `RESPAN_BASE_URL`, `RESPAN_MODEL`.

Run:

```bash
npm install
npm run all
```

Examples:

- `01_gateway_basic.ts`: basic agent run through the Respan gateway.
- `02_gateway_tool.ts`: function tool call and tool result tracing.
- `03_gateway_agent_as_tool.ts`: nested agent exposed as a tool.
- `04_gateway_handoff.ts`: triage agent handing off to a specialist agent.
- `05_gateway_guardrails.ts`: input and output guardrail execution.
- `06_gateway_structured_session.ts`: Zod structured output plus `MemorySession`.
- `07_gateway_streaming_lifecycle.ts`: streaming run events and lifecycle hooks.

## Semantic edge-case example

`complex-edge-cases.ts` exercises nested tools, handoffs, guardrails, structured output, errors, and large payloads through the same Respan gateway setup. Run it with `npm run complex`.
