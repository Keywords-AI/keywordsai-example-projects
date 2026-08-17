# Mistral AI tracing examples

These examples trace the official `mistralai` Python SDK with Respan. They load
environment variables from the repository root `.env` file.

Required for exporting traces:

```bash
RESPAN_API_KEY=...
```

Install the registry dependencies from this directory:

```bash
python -m pip install -r requirements.txt
```

For repository development and validation, link the local packages after that
registry install:

```bash
python -m pip install -e ../../../../respan/python-sdks/respan-sdk
python -m pip install -e ../../../../respan/python-sdks/respan-tracing
python -m pip install -e ../../../../respan/python-sdks/respan
python -m pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-openinference
python -m pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-mistralai
```

For Mistral calls, use one of these options:

```bash
# Direct Mistral API calls, still traced to Respan
MISTRAL_API_KEY=...
```

If `MISTRAL_API_KEY` is not set, the examples route the Mistral SDK through the
Respan OpenAI-compatible gateway using `RESPAN_GATEWAY_API_KEY` or
`RESPAN_API_KEY`. In gateway mode, `RESPAN_MISTRALAI_MODEL` is used when set;
otherwise the scripts fall back to `RESPAN_MODEL` from the repo-root `.env` so
the examples run in this repository without requiring separate Mistral provider
credentials.

Optional environment variables:

```bash
RESPAN_BASE_URL=https://api.respan.ai/api
RESPAN_MISTRALAI_MODEL=mistral/mistral-small
MISTRALAI_MODEL=mistral/mistral-small
```

Run one script at a time:

```bash
python 01_chat_completion.py
python 02_multi_turn_chat.py
python 03_async_chat_completion.py
python 04_sync_streaming.py
python 05_async_streaming.py
python 06_tool_calling.py
python 07_expected_provider_failure.py
python 08_expected_application_failure.py
```

Or run the complete committed suite with one exact marker:

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-fix-py-group-19-YYYYMMDDTHHMMSSZ python run_all.py
```

When the variable is omitted, `run_all.py` creates and prints one parent marker,
then passes that same marker to all eight child processes.

The first three examples use the configured live gateway (or direct Mistral
credentials). The stream, tool, and failure examples use the current Mistral
SDK with deterministic HTTP fixtures so their content, usage, tool calls, and
errors are repeatable while the resulting spans are still exported to Respan.

Each script preserves `RESPAN_EXAMPLE_RUN_ID` in metadata as
`example_run_id`, and also emits a unique per-scenario `custom_identifier`.
Every workflow accepts bounded JSON-native scenario input; live SDK clients are
captured outside decorated signatures.
