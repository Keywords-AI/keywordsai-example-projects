# Logs to Trace Example (TypeScript)

This example demonstrates how to send trace logs to KeywordsAI while avoiding ID collisions by processing existing trace data.

As long as the following conditions are met:

- Proper timestamps of each span are tracked
- Trace, span ids are properly assigned and correctly representing parent-child relationship

A list of logs will be aggregated into a trace automatically upon ingestion

Learn more about the [Logging API](https://docs.keywordsai.co/api-endpoints/integration/request-logging-endpoint)

## How this example works

1. Loads sample trace data from `trace_logs.json`
2. Shifts timestamps to current time while preserving relative timing
3. Remaps trace and span IDs to prevent conflicts with existing traces
4. Sends processed logs to KeywordsAI traces endpoint

## Setup

From the `typescript` directory:

```bash
yarn install
```

Set environment variables (create a `.env` file or export them):

- `KEYWORDSAI_API_KEY`: Your KeywordsAI API key
- `KEYWORDSAI_BASE_URL`: KeywordsAI base URL

## Usage

```bash
npx tsx basic/logs_to_trace/main.ts
```

Or from the project root:

```bash
cd example_scripts/typescript
npx tsx basic/logs_to_trace/main.ts
```
