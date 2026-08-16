import assert from "node:assert/strict";
import test from "node:test";

import { resolveCaseIdentifiers } from "../vercel-common.mjs";

test("shared audit marker remains exact while case identifiers stay unique", () => {
  const marker = "otel2-fix-js-group-05-test";
  const first = resolveCaseIdentifiers("generate-text", { RESPAN_EXAMPLE_RUN_ID: marker }, 1);
  const second = resolveCaseIdentifiers("tool-call", { RESPAN_EXAMPLE_RUN_ID: marker }, 2);

  assert.equal(first.auditRunId, marker);
  assert.equal(second.auditRunId, marker);
  assert.notEqual(first.runId, second.runId);
  assert.match(first.runId, /generate-text/);
  assert.match(second.runId, /tool-call/);
});

test("standalone runs fall back to their unique case identifier", () => {
  const identifiers = resolveCaseIdentifiers("embed", {}, 123);
  assert.equal(identifiers.auditRunId, identifiers.runId);
});
