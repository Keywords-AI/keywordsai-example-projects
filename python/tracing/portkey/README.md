# Portkey tracing

The deterministic suite uses the real current Portkey SDK against a bounded
OpenAI-compatible protocol fixture. It covers sync, async, streaming, a
connected two-turn tool execution, and a provider-style 401. The optional live
script runs only when `PORTKEY_API_KEY` is configured.

```bash
python -m pip install -r requirements.txt
RESPAN_EXAMPLE_RUN_ID=portkey-check python run_all.py
```

For local package development, install the registry requirements first and
then link the instrumentation explicitly:

```bash
python -m pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-portkey
```

Every script preserves the exact shell marker, uses only bounded semantic
workflow arguments, closes its Portkey client, and flushes/shuts down Respan.
The aggregate runner continues through failures and timeouts.
