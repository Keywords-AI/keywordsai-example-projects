# Vertex AI OTel 2.x tracing examples

The first five scripts patch the public methods on the installed
`google-cloud-aiplatform` 1.164.x classes with deterministic responses before
activating Respan. This verifies the current real class boundary without
requiring Google credentials. The set covers generation, streaming, async,
connected tool execution, and an exact provider 503.

`06_live_provider.py` uses the real Vertex service when
`GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` are configured; otherwise
it exits with an explicit skip.

The exact caller-supplied `RESPAN_EXAMPLE_RUN_ID` is retained in `run_id` and
`example_run_id` metadata on every deterministic record.

Run all examples with one marker:

```bash
RESPAN_EXAMPLE_RUN_ID=my-exact-marker python run_all.py
```

The runner applies a per-process timeout, continues through failures, and
returns nonzero if any script fails.
