# OpenInference Contract Examples

These deterministic examples validate the generic
`respan-instrumentation-openinference` translation boundary without depending
on a vendor API. They emit standard OpenInference attributes through the real
OpenTelemetry provider and Respan exporter, covering:

- chat content, provider identity, model, and provider-reported usage;
- tool definitions, current-turn tool calls, and a connected tool execution;
- embedding input, model, usage, and vector output;
- an expected OTel `ERROR` with no synthetic usage;
- streaming metadata plus bounded, redacted input/output content.

Each script creates one named workflow, inherits the exact
`RESPAN_EXAMPLE_RUN_ID` marker when supplied, loads credentials from the
repository `.env` without overriding the shell, and explicitly flushes and
shuts down Respan.

## Install from the registry

```bash
cd python/tracing/openinference
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Validate a local `respan` checkout

Keep `requirements.txt` registry-portable, then overlay editable local packages:

```bash
python -m pip install -e ../../../../respan/python-sdks/respan-sdk
python -m pip install -e ../../../../respan/python-sdks/respan-tracing
python -m pip install -e ../../../../respan/python-sdks/respan
python -m pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-openinference
```

## Run

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-openinference-check python run_all.py
```

The runner executes all five scripts, prints each exit code, and returns nonzero
if any process fails. Expected output is five traces containing 11 records: one
workflow root per script, five translated OpenInference operations, and one tool
execution child.
