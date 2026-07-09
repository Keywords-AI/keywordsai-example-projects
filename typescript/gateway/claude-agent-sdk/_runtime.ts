import * as _ClaudeAgentSDK from "@anthropic-ai/claude-agent-sdk";
import { Respan } from "@respan/respan";
import { ClaudeAgentSDKInstrumentor } from "@respan/instrumentation-claude-agent-sdk";

const API_KEY = process.env.RESPAN_API_KEY;
const BASE_URL = (process.env.RESPAN_BASE_URL || "https://api.respan.ai/api").replace(/\/+$/, "");

if (!API_KEY) {
  throw new Error("Set RESPAN_API_KEY");
}

const ClaudeAgentSDK = { ..._ClaudeAgentSDK };
const respan = new Respan({
  apiKey: API_KEY,
  baseURL: process.env.RESPAN_BASE_URL,
  instrumentations: [new ClaudeAgentSDKInstrumentor({ sdkModule: ClaudeAgentSDK, agentName: "claude-agent-sdk" })],
});
await respan.initialize();

export { API_KEY, BASE_URL, ClaudeAgentSDK };
