# Langfuse tracing with Respan

This bounded example uses the current Langfuse Python SDK and the linked
`respan-instrumentation-langfuse` package. It creates two deterministic traces:

- `langfuse_simple.workflow`: workflow to generation
- `langfuse_research.workflow`: workflow to two tools and one generation

The generation spans include model, prompt/completion content, and exact token
usage. Dummy Langfuse credentials are used only to enable local SDK span
creation; the Respan instrumentor intercepts Langfuse's exporter before any
request is sent to Langfuse.

Install the requirements and the local package, then run:

    RESPAN_EXAMPLE_RUN_ID=your-marker python langfuse_simple_example.py

The script loads the repository root `.env`, never prints credentials, flushes
both SDKs in `finally`, and fails unless all six expected Langfuse spans pass
through the local instrumentation package.
