# Respan Example Projects

Example projects demonstrating [Respan](https://respan.ai) tracing, observability, and platform integrations.

## Structure

```
python/
  tracing/
    respan-tracing-sdk/       # Core respan-tracing SDK examples (basic usage, span operations, async, debug logging, medical agent)
    openai-agents-sdk/        # OpenAI Agents SDK with Respan tracing (basic, patterns, handoffs, gateway, guardrails)
    openai-sdk/               # OpenAI SDK direct integration (completions, responses, streaming, batch, tools)
    anthropic-agents-sdk/     # Anthropic Agents SDK with Respan tracing (basic, sessions, streaming, tools)
    crewai/                   # CrewAI integration example
    langfuse/                 # Langfuse integration (decorators, generation tracing, nested traces)
    instructor/               # Instructor library example
    langchain/                # LangChain agent example
    pydantic-ai/              # Pydantic AI example
    legacy/
      braintrust/             # Legacy Braintrust exporter quickstart
      haystack/               # Legacy Haystack exporter examples
  gateway/
    google-genai/             # Google Gemini SDK example
    anthropic-agents/         # Anthropic Agents gateway example
    openai-agents/            # OpenAI Agents gateway example
  dev-tools/
    claude-code/              # Claude Code tracing hook
    cursor/                   # Cursor IDE tracing hook

typescript/
  tracing/
    respan-tracing-sdk/       # Core @respan/tracing SDK examples (basic, advanced, span management, instrumentation, noise filtering)
      nextjs-openai/          # Next.js + OpenAI with @respan/tracing directly
    openai-agents-sdk/        # OpenAI Agents SDK with Respan tracing
    openai-sdk/               # OpenAI SDK direct integration (attributes, decorators, hello world)
    anthropic-agents-sdk/     # Anthropic Agents SDK with Respan tracing (hello world, tools)
    anthropic-openinference/  # Anthropic OpenInference integration
    vercel-tracing/           # Vercel AI SDK + Next.js with @respan/exporter-vercel
    mastra/                   # Mastra framework with @respan/exporter-vercel
    legacy/
      vercel-exporter/        # Legacy Vercel exporter quickstart
      openai-agents-exporter/ # Legacy OpenAI Agents exporter (agent patterns, MCP, tools, realtime, Next.js)
  gateway/
    google-genai/             # Google Gemini SDK example
    anthropic-agents-sdk/     # Anthropic Agents SDK gateway example

fullstack/
  vercel-ai-fastapi/          # Next.js frontend + FastAPI backend with Respan tracing

platform/
  sdk-examples/               # Respan SDK workflow examples (datasets, experiments, prompts, evaluators, logs)
    python/                   # Python SDK examples
    typescript/               # TypeScript SDK examples
  demo-setup-python/          # Python scripts for demo account setup
  demo-setup-typescript/      # TypeScript scripts for demo account setup
  experiments/                # Experiment workflow notebooks
  multi-modal-evals/          # Multi-modal tool evaluation workflows
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
