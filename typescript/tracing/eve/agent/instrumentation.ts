import {
  EveInstrumentor,
  withEveLineage,
} from "@respan/instrumentation-eve";
import { Respan } from "@respan/respan";
import { defineInstrumentation } from "eve/instrumentation";
import {
  EXAMPLE_RUN_ID,
  RESPAN_API_KEY,
  RESPAN_BASE_URL,
} from "../_env.js";

const respan = new Respan({
  apiKey: RESPAN_API_KEY,
  baseURL: RESPAN_BASE_URL,
  appName: "eve-typescript-examples",
  instrumentations: [new EveInstrumentor()],
  // These examples use only deterministic synthetic content, so keep capture
  // enabled and verify the actual chat/tool payloads on the platform.
  traceContent: true,
  silenceInitializationMessage: true,
});

await respan.initialize();

export default withEveLineage(
  defineInstrumentation({
    functionId: "eve_typescript_" + EXAMPLE_RUN_ID,
    recordInputs: true,
    recordOutputs: true,
    events: {
      "step.started"(input) {
        return {
          runtimeContext: {
            "example.framework": "eve",
            "example.run_id": EXAMPLE_RUN_ID,
            "example.step_index": input.step.index,
          },
        };
      },
    },
  }),
);
