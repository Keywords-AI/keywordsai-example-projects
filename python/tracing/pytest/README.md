# Pytest OTel 2.x tracing examples

This suite runs the real Pytest plugin in three isolated processes: normal outcomes (pass, parameterization, skip, xfail, and a nested Respan task), a deliberate assertion failure, and a content-disabled privacy failure.

```bash
pip install -r requirements.txt
python run_all.py
```

For local instrumentation development, install `respan-instrumentation-pytest`, `respan-ai`, `respan-tracing`, and `respan-sdk` editable from the sibling `respan` checkout. The committed requirements remain registry-portable.

`run_all.py` loads the repository `.env` without overriding shell values, establishes one `RESPAN_EXAMPLE_RUN_ID`, accepts the two expected Pytest exit-code 1 results, continues after timeouts/failures, and returns nonzero only when a scenario violates its expected contract.
