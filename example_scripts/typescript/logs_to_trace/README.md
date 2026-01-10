# KeywordsAI Tracing Example

This directory contains a TypeScript example for KeywordsAI's tracing functionality using the `@keywordsai/tracing` SDK.

## Setup

1. **Install dependencies**:
   Navigate to the `example_scripts/typescript` directory and install the required packages:
   ```bash
   yarn install
   # Or if you need to add the tracing SDK and OpenAI explicitly:
   yarn add @keywordsai/tracing openai
   ```

2. **Configure environment variables**:
   Create a `.env` file in this directory (`example_scripts/typescript/logs_to_trace/`) using `.env.example` as a template:
   ```bash
   KEYWORDSAI_API_KEY=your_keywordsai_api_key
   KEYWORDSAI_BASE_URL=https://api.keywordsai.co
   
   # Using Keywords AI as an LLM Gateway for tracing
   OPENAI_API_KEY=your_keywordsai_api_key
   OPENAI_BASE_URL=https://api.keywordsai.co/api
   ```

## Usage

### Run Tracing Test (`test-tracing.ts`)

This script demonstrates a multi-task workflow ("Pirate Joke Workflow") with nested tracing:
1. **Joke Creation**: Generates a joke about OpenTelemetry.
2. **Pirate Translation**: Translates the joke into pirate speak.
3. **Signature Generation**: Adds a creative pirate signature.

Run the test from the `typescript` directory using `tsx`:
```bash
npx tsx logs_to_trace/test-tracing.ts
```

## Viewing Results

After running the test, navigate to the **Traces** tab on the KeywordsAI platform to see your workflow, tasks, and LLM calls visualized.
