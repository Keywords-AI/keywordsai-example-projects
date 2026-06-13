# Google ADK TypeScript tracing

Examples for `@respan/instrumentation-google-adk` with the Google ADK TypeScript SDK.

The scripts use a deterministic local ADK `BaseLlm` so they do not require a Gemini key. They still exercise ADK's real runner, agent, LLM, tool, streaming, and OpenTelemetry code paths. Respan export uses `RESPAN_API_KEY` from the `respan-example-projects/.env` file.

The shared runner initializes Respan before dynamically importing `@google/adk`; this import order is required because ADK creates its OpenTelemetry tracer at module load time.

## Run

```bash
npm install
npm run all
```

## Examples

- `01_hello_world.ts`: runner, workflow, agent, and chat span
- `02_tool_use.ts`: model-requested tool call and tool span
- `03_streaming_attributes.ts`: streaming LLM response with Respan propagation metadata
