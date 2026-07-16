# Semantic Kernel tracing examples

These examples run Microsoft Semantic Kernel through Respan tracing and the
Respan gateway. They cover direct kernel function invocation, chat completion,
automatic plugin/tool invocation, and a deterministic failing function.

The scripts load environment variables from the examples repo root `.env` file:

- `RESPAN_API_KEY`
- `RESPAN_BASE_URL`
- `RESPAN_GATEWAY_API_KEY`
- `RESPAN_GATEWAY_BASE_URL`
- `RESPAN_MODEL`

Run from this directory after installing local packages:

```bash
python 01_kernel_function.py
python 02_chat_completion.py
python 03_plugin_tool_call.py
python 04_function_failure.py
```
