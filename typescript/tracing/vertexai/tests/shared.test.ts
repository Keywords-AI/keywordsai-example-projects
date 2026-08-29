import assert from "node:assert/strict";
import test from "node:test";

import { flushAndShutdown } from "../_shared.js";

test("flushAndShutdown awaits delayed exporter shutdown", async () => {
  const events: string[] = [];
  let releaseShutdown: (() => void) | undefined;
  const shutdownGate = new Promise<void>((resolve) => {
    releaseShutdown = resolve;
  });
  const runtime = {
    async shutdown(): Promise<void> {
      events.push("started");
      await shutdownGate;
      events.push("finished");
    },
  };

  const cleanup = flushAndShutdown(runtime);
  await Promise.resolve();
  assert.deepEqual(events, ["started"]);

  releaseShutdown?.();
  await cleanup;
  assert.deepEqual(events, ["started", "finished"]);
});
