import * as _ClaudeAgentSDK from "@anthropic-ai/claude-agent-sdk";
import { Respan } from "@respan/respan";
import { ClaudeAgentSDKInstrumentor } from "@respan/instrumentation-claude-agent-sdk";

export const ClaudeAgentSDK = { ..._ClaudeAgentSDK };

export const QUERY_TIMEOUT_SECONDS = Number.parseInt(
  process.env.RESPAN_QUERY_TIMEOUT_SECONDS ?? "90",
  10,
);

type QueryMessage = Record<string, unknown>;
type MessageHandler = (
  message: QueryMessage,
  context: { sessionId?: string },
) => Promise<void> | void;

let respanInit: Promise<Respan> | undefined;

export function initializeRespan(): Promise<Respan> {
  if (!respanInit) {
    const respan = new Respan({
      apiKey: process.env.RESPAN_API_KEY,
      baseURL: process.env.RESPAN_BASE_URL,
      instrumentations: [
        new ClaudeAgentSDKInstrumentor({
          sdkModule: ClaudeAgentSDK,
          agentName: "claude-agent-sdk",
        }),
      ],
    });
    respanInit = respan.initialize().then(() => respan);
  }
  return respanInit;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

interface QueryForResultOptions {
  prompt: string;
  options: unknown;
  onMessage?: MessageHandler;
  timeoutSeconds?: number;
}

interface QueryForResultResult {
  result: QueryMessage;
  sessionId?: string;
  messageTypes: string[];
}

export async function queryForResult(
  params: QueryForResultOptions,
): Promise<QueryForResultResult> {
  await initializeRespan();

  const timeoutSeconds = params.timeoutSeconds ?? QUERY_TIMEOUT_SECONDS;
  const messageTypes: string[] = [];
  let sessionId: string | undefined;
  let result: QueryMessage | undefined;
  let timedOut = false;

  const stream = (await ClaudeAgentSDK.query({
    prompt: params.prompt,
    options: params.options as any,
  })) as AsyncGenerator<unknown, void, unknown>;

  const timeoutId = setTimeout(() => {
    timedOut = true;
    void stream.return?.(undefined);
  }, Math.max(1, timeoutSeconds) * 1000);

  try {
    try {
      for await (const rawMessage of stream) {
        const message = rawMessage as QueryMessage;
        const msgType = String(message.type ?? "unknown");
        messageTypes.push(msgType);

        if (message.type === "system") {
          const data = (message.data ?? {}) as Record<string, unknown>;
          const maybeSessionId = data.session_id ?? data.sessionId ?? sessionId;
          if (typeof maybeSessionId === "string") {
            sessionId = maybeSessionId;
          }
        }
        if (message.type === "result") {
          const maybeSessionId = message.session_id ?? sessionId;
          if (typeof maybeSessionId === "string") {
            sessionId = maybeSessionId;
          }
          result = message;
        }

        if (params.onMessage) {
          await params.onMessage(message, { sessionId });
        }
      }
    } catch (error) {
      if (!result) {
        throw error;
      }
    }
  } finally {
    clearTimeout(timeoutId);
    await sleep(250);
  }

  if (timedOut) {
    throw new Error(`Timed out after ${timeoutSeconds}s waiting for query result.`);
  }
  if (!result) {
    throw new Error("Query completed without a result message.");
  }

  return { result, sessionId, messageTypes };
}
