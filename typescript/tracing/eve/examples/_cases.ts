import { type Client } from "eve/client";
import { runCase, type ExampleResult } from "./_shared.js";

export function runBasicTurn(client: Client): Promise<ExampleResult> {
  return runCase(
    client,
    "basic-turn",
    "RESPAN_EVE_BASIC: return the deterministic basic response.",
    {
      eventTypes: ["message.completed", "session.waiting"],
      message: /Eve basic instrumentation example completed/,
    },
  );
}

export function runToolCall(client: Client): Promise<ExampleResult> {
  return runCase(
    client,
    "tool-call",
    "RESPAN_EVE_TOOL: call get_weather and report its deterministic result.",
    {
      eventTypes: ["actions.requested", "action.result", "session.waiting"],
      message: /Sunny/,
    },
  );
}

export function runSubagentLineage(client: Client): Promise<ExampleResult> {
  return runCase(
    client,
    "subagent-lineage",
    "RESPAN_EVE_SUBAGENT: call researcher and include its exact marker.",
    {
      eventTypes: ["subagent.called", "subagent.completed", "session.waiting"],
      message: /RESEARCH_MARKER=eve-lineage-ok/,
      needsChildSession: true,
    },
  );
}
