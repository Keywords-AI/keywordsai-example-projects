# Claude Agent SDK TypeScript

Gateway-first examples for `@anthropic-ai/claude-agent-sdk@0.3.201` with `@respan/instrumentation-claude-agent-sdk`.

Set `RESPAN_API_KEY` in `respan-example-projects/.env`. Optional overrides: `RESPAN_GATEWAY_API_KEY`, `RESPAN_GATEWAY_BASE_URL`, `RESPAN_BASE_URL`.

Run:

```bash
npm install
npm run all
```

Examples:

- `01_gateway_basic.ts`: basic `query` stream through the Respan gateway.
- `02_gateway_tool.ts`: built-in tool execution.
- `03_gateway_structured_options.ts`: custom main-thread agent, JSON schema output, hook events, and partial-message streaming.
- `04_gateway_mcp_tool.ts`: in-process SDK MCP server and MCP tool call.
- `05_gateway_hooks_permissions.ts`: `PreToolUse`/`PostToolUse` hooks and `canUseTool`.
- `06_gateway_options_session.ts`: explicit session ID, custom system prompt, thinking, effort, and partial messages.
