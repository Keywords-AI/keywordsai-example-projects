import assert from "node:assert/strict";
import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";
import { once } from "node:events";
import { fileURLToPath } from "node:url";
import { Client, type HandleMessageStreamEvent } from "eve/client";
import { EXAMPLE_RUN_ID } from "../_env.js";

type EveEventType = HandleMessageStreamEvent["type"];

const EXAMPLE_ROOT = fileURLToPath(new URL("..", import.meta.url));
const EVE_BIN = fileURLToPath(
  new URL("../node_modules/eve/bin/eve.js", import.meta.url),
);
const HOST = "127.0.0.1";
const PORT = Number(process.env.EVE_EXAMPLE_PORT ?? 23821);
const SERVER_URL = "http://" + HOST + ":" + PORT;

export interface ExampleResult {
  readonly caseId: string;
  readonly childSessionIds: readonly string[];
  readonly eventTypes: readonly EveEventType[];
  readonly message: string;
  readonly runId: string;
  readonly sessionId: string;
  readonly status: string;
}

export async function runWithEveServer(
  runCases: (client: Client) => Promise<readonly ExampleResult[]>,
): Promise<void> {
  const server = startEveServer();
  const client = new Client({ host: SERVER_URL });

  try {
    await waitForHealth(client, server);
    const results = await runCases(client);
    console.log(
      JSON.stringify(
        {
          framework: "eve",
          functionId: "eve_typescript_" + EXAMPLE_RUN_ID,
          runId: EXAMPLE_RUN_ID,
          results,
        },
        null,
        2,
      ),
    );

    // Respan uses a batch processor. Leave the real Eve server alive long
    // enough for its worker to export before the controlled shutdown.
    await delay(Number(process.env.RESPAN_EXAMPLE_EXPORT_WAIT_MS ?? 8_000));
  } finally {
    await stopEveServer(server);
  }
}

export async function runCase(
  client: Client,
  caseId: string,
  prompt: string,
  expected: {
    readonly eventTypes: readonly EveEventType[];
    readonly message: RegExp;
    readonly needsChildSession?: boolean;
  },
): Promise<ExampleResult> {
  const session = client.session();
  const response = await session.send(prompt);
  const result = await response.result();
  const eventTypes = result.events.map((event) => event.type);
  const childSessionIds = collectChildSessionIds(result.events);

  assert.equal(result.status, "waiting");
  assert.match(result.message ?? "", expected.message);
  for (const eventType of expected.eventTypes) {
    assert.ok(
      eventTypes.includes(eventType),
      caseId + " did not emit " + eventType + ": " + eventTypes.join(", "),
    );
  }
  if (expected.needsChildSession) {
    assert.ok(
      childSessionIds.length > 0,
      caseId + " did not expose a child session id",
    );
  }

  return {
    caseId,
    childSessionIds,
    eventTypes,
    message: result.message ?? "",
    runId: EXAMPLE_RUN_ID,
    sessionId: result.sessionId,
    status: result.status,
  };
}

function collectChildSessionIds(
  events: readonly HandleMessageStreamEvent[],
): readonly string[] {
  return events.flatMap((event) =>
    event.type === "subagent.called"
      ? [event.data.childSessionId]
      : [],
  );
}

function startEveServer(): ChildProcessWithoutNullStreams {
  const child = spawn(
    process.execPath,
    [EVE_BIN, "start", "--host", HOST, "--port", String(PORT)],
    {
      cwd: EXAMPLE_ROOT,
      env: {
        ...process.env,
        RESPAN_EXAMPLE_RUN_ID: EXAMPLE_RUN_ID,
        RESPAN_SPAN_NAME_STYLE: "semantic",
      },
      stdio: ["pipe", "pipe", "pipe"],
    },
  );

  if (process.env.RESPAN_EXAMPLE_DEBUG === "true") {
    child.stdout.pipe(process.stdout);
    child.stderr.pipe(process.stderr);
  }
  return child;
}

async function waitForHealth(
  client: Client,
  server: ChildProcessWithoutNullStreams,
): Promise<void> {
  const deadline = Date.now() + 120_000;
  let lastError: unknown;

  while (Date.now() < deadline) {
    if (server.exitCode !== null) {
      throw new Error(
        "eve start exited before it became healthy (" + server.exitCode + ")",
      );
    }
    try {
      await client.health();
      return;
    } catch (error) {
      lastError = error;
      await delay(500);
    }
  }

  throw new Error("Timed out waiting for eve start: " + String(lastError));
}

async function stopEveServer(
  server: ChildProcessWithoutNullStreams,
): Promise<void> {
  if (server.exitCode !== null) {
    return;
  }

  server.kill("SIGTERM");
  await Promise.race([once(server, "exit"), delay(10_000)]);
  if (server.exitCode === null) {
    server.kill("SIGKILL");
    await once(server, "exit");
  }
}

function delay(milliseconds: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}
