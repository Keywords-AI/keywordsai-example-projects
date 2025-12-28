# KeywordsAI Tracing Demo

A Next.js demo application showcasing KeywordsAI tracing features for OpenAI using the Vercel AI SDK.

## Example Groups

This demo is organized into three core showcase areas:

1.  **Basic Trace & Workflow**: Combines **Quickstart**, **Metadata/Params** (Customer ID & Group ID), and **Agent Handoff** (Multi-step triage) into a single execution.
2.  **Tool Use**: Demonstrates an agent interacting with external functions (e.g., Weather Tool).
3.  **Override Span**: Shows how to customize trace names and data for specific spans.

## Getting Started

## Recommended: run locally with env vars

This demo is simplest (and safest) when you run it locally with environment variables.

Docs: [KeywordsAI Vercel AI SDK tracing docs](https://docs.keywordsai.co/integration/development-frameworks/tracing/vercel-tracing?utm_source=agentblocks)

## Local setup

### Prerequisites

- Node.js 18+
- OpenAI API key
- KeywordsAI API key ([Get one here](https://platform.keywordsai.co))

### Install

```bash
yarn install
```

> **Note**: This project uses traditional `node_modules` for Turbopack compatibility.

### Configure env vars

Create a `.env.local` file in `example_scripts/vercel/`:

```bash
# KeywordsAI Configuration (enables tracing)
KEYWORDSAI_API_KEY=your_keywordsai_api_key_here
KEYWORDSAI_BASE_URL=https://api.keywordsai.co  # optional

# OpenAI Configuration (enables model calls)
OPENAI_API_KEY=your_openai_api_key_here
```

### Run

```bash
yarn dev
```

Open `http://localhost:3000` and click a card to run a demo trace.

## Deploy to Vercel

### Option A (recommended): use Vercel env vars

1. Create a Vercel project from this folder (`example_scripts/vercel/`).
2. In Vercel Project Settings → Environment Variables, add:
   - `OPENAI_API_KEY`
   - `KEYWORDSAI_API_KEY`
   - `KEYWORDSAI_BASE_URL` (optional)
3. Deploy.

This is the most reliable option (especially for tracing), because serverless instances don’t share in-memory state.

### Option B (demo-only): paste keys into the UI

The UI has an **API Keys (optional)** panel:

- Keys are **not persisted** (refresh clears them).
- If you set env vars (`OPENAI_API_KEY`, `KEYWORDSAI_API_KEY`) you **don’t need** the UI fields.
- OpenAI key is sent per request via the `x-openai-api-key` header.
- KeywordsAI key is sent per request via the `x-keywordsai-api-key` header.

> **Note**: For production tracing, use Vercel env vars (Option A). The UI KeywordsAI key is best-effort and may not work reliably across serverless instances.

## Security notes

- Never commit secrets. This repo ignores `.env*` via `.gitignore`.
- The UI key inputs are convenient for demos, but they still send secrets over the network to your deployed server. Treat them as sensitive.

## Project Structure

```
app/
  api/
    openai/
      basic-workflow/      # Combined Handoff + Metadata demo
      tool-use/            # Agent with tools demo
      override-span/       # Custom span data demo
  page.tsx                 # Main Showcase UI
instrumentation.ts         # KeywordsAI tracing setup
```

## Learn More

- [KeywordsAI Vercel AI SDK tracing docs](https://docs.keywordsai.co/integration/development-frameworks/tracing/vercel-tracing?utm_source=agentblocks)
- [Vercel AI SDK Tracing](https://ai-sdk.dev/docs/advanced/telemetry)
