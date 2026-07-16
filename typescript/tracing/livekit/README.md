# LiveKit Agents + Respan Examples (TypeScript)

Runnable examples for tracing LiveKit Agents TypeScript sessions with Respan.

These examples load environment variables from the repository root `.env` file.

## Setup

```bash
cd typescript/tracing/livekit
npm install
```

Required root `.env` value:

| Variable | Required | Description |
| --- | --- | --- |
| `RESPAN_API_KEY` | Yes | Respan API key for trace export. |
| `RESPAN_BASE_URL` | No | Defaults to Respan production API. |
| `RESPAN_EXAMPLE_RUN_ID` | No | Optional run id for exact trace lookup. |

## Run

```bash
npm run all
```

Individual scripts:

- `01_text_agent_turn.ts`: traces a LiveKit `AgentSession`, agent activity, agent turn, and LLM node.
- `02_tool_call.ts`: traces LiveKit function tool execution and the follow-up model turn.
- `03_agent_handoff.ts`: traces a LiveKit agent handoff through a function tool.

Each script prints a workflow name and run id that can be used to find the trace in Respan.
