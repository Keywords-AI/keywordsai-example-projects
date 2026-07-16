# Respan Example Projects

Example projects demonstrating [Respan](https://respan.ai) tracing, observability, and platform integrations.

## Structure

```
python/
  tracing/
    respan-tracing-sdk/   # Core respan-tracing SDK examples (basic usage, span operations, multi-provider)
    openai-agents-sdk/    # OpenAI Agents SDK with Respan tracing (basic, patterns, handoffs, tools, research bot)
    claude-agent-sdk/     # Claude Agent SDK with Respan tracing
    dspy/                 # DSPy native instrumentation examples
    langfuse/             # Langfuse integration example
    instructor/           # Instructor library example
    langchain/            # LangChain agent example
    cursor-sdk/           # Cursor SDK hook replay tracing examples
  gateway/
    google-genai/         # Google Gemini SDK example
  dev-tools/
    claude-code/          # Claude Code tracing hook
    cursor/               # Cursor IDE tracing hook

typescript/
  tracing/
    respan-tracing-sdk/   # Core @respan/tracing SDK examples (basic, advanced, span management, multi-provider)
      nextjs-openai/      # Next.js + OpenAI with @respan/tracing directly
    claude-agent-sdk/     # Claude Agent SDK with Respan tracing
    vercel-tracing/       # Vercel AI SDK + Next.js with @respan/exporter-vercel
    mastra/               # Mastra framework with @respan/exporter-vercel
  gateway/
    google-genai/         # Google Gemini SDK example

fullstack/
  vercel-ai-fastapi/      # Next.js frontend + FastAPI backend with Respan tracing

platform/
  demo-setup-python/      # Python scripts for demo account setup (logging, datasets, evaluators, prompts)
  demo-setup-typescript/  # TypeScript scripts for demo account setup
  experiments/            # Experiment workflow notebooks
  multi-modal-evals/      # Multi-modal tool evaluation workflows
```

## Getting Started

1. Clone this repository
2. Navigate to the example you want to run
3. Follow the README in each directory for setup instructions

## Documentation

- [Respan Docs](https://www.respan.ai/docs) - Full documentation
- [Python Tracing SDK](https://www.respan.ai/docs/sdks/python/tracing/quickstart) - Python SDK quickstart
- [TypeScript Tracing SDK](https://www.respan.ai/docs/sdks/typescript/tracing/quickstart) - TypeScript SDK quickstart
- [Integrations](https://www.respan.ai/docs/integrations/overview) - Integration guides
