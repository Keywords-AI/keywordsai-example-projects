# Eve TypeScript tracing examples

This example set runs Eve 0.26.1 with
@respan/instrumentation-eve against the local Respan workspace.
It uses the documented deterministic mockModel from Eve, so no model-provider
key is required, while still exercising the real Eve server, AI SDK telemetry,
tool loop, and delegated subagent session.

The three cases cover:

- a basic Eve turn and model call;
- an authored get_weather tool call;
- a declared researcher subagent with root and child session lineage.

agent/instrumentation.ts activates only EveInstrumentor, composes
withEveLineage, and enables model input/output capture because every payload in
this example is deterministic synthetic data. Do not activate VercelAIInstrumentor
in the same Eve process.

## Requirements

- Node.js 24 or newer
- RESPAN_API_KEY in respan-example-projects/.env
- optional RESPAN_BASE_URL

## Install and validate

The local instrumentation currently uses workspace dependencies. Keep the
file-linked Respan packages as symlinks during local validation:

    npm install --install-links=false
    npm run typecheck
    npm run info
    npm run build

Run all three live cases:

    RESPAN_EXAMPLE_RUN_ID=eve-ts-local npm run examples

Or run one case with npm run example:basic, npm run example:tool, or
npm run example:subagent.

The runner builds the app and starts eve start on 127.0.0.1:23821, waits for its health
route, drives real sessions through eve/client, prints the root and child
session IDs, waits for the Respan batch exporter, and shuts the server down.
Override the port with EVE_EXAMPLE_PORT.

For platform verification, query Respan with the printed unique run ID. The
instrumentation uses eve_typescript_<run-id> as its function ID and also
records the run ID in Eve runtime-context metadata. The function ID is exported
as the workflow name on the turn, chat, tool, task, and subagent spans.

One complete batch must produce exactly three traces, one for each case. In
semantic span-name mode, their expected trees are:

    basic
    agent
    └── task
        └── llm.<model>

    tool
    agent
    ├── task
    │   ├── llm.<model>  (tool request)
    │   └── tool.get_weather
    └── task
        └── llm.<model>  (final response)

    delegated subagent
    agent
    ├── task
    │   └── llm.<root-model>  (delegation request)
    ├── agent
    │   └── task
    │       └── llm.<researcher-model>
    └── task
        └── llm.<root-model>  (final response)

The child Eve session is part of the third trace, not a fourth trace, and the
late usage-only event is not exported after exact lineage correlation. Verify
that every span has the workflow name, every chat span has non-empty serialized
input and output (a tool-request output carries `tool_calls` with empty text),
and `tool.get_weather` has both structured arguments and its structured
result.
