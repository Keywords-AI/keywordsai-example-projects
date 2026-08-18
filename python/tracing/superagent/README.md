# Superagent Tracing Examples

These examples trace the Superagent `safety-agent` SDK with
`respan-instrumentation-superagent`.

Each script wraps the run in a Respan workflow whose name matches the script
filename, so the platform result is easy to map back to the example.

## Setup

Install portable registry requirements and run the complete set with one exact
marker:

```bash
pip install -r requirements.txt
RESPAN_EXAMPLE_RUN_ID=superagent-check python run_all.py
```

For local package development, link the package after installing requirements:

```bash
pip install -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-superagent
```

The scripts load the `.env` file from the `respan-example-projects` repo root.
They use `RESPAN_API_KEY`, `RESPAN_BASE_URL`, `RESPAN_GATEWAY_API_KEY`,
`RESPAN_GATEWAY_BASE_URL`, and `RESPAN_MODEL` when present.

`04_scan.py` requires `DAYTONA_API_KEY` and is skipped when that key is absent.

## Examples

| Script | Description |
| ------ | ----------- |
| `01_guard.py` | Runs and traces a Superagent guardrail check. |
| `02_redact.py` | Runs and traces a PII redaction operation. |
| `03_workflow.py` | Nests Superagent operations under Respan workflow/task spans. |
| `04_scan.py` | Runs a repository scan when Daytona credentials are available. |
| `05_expected_error.py` | Records a bounded provider/model error. |

Every example preserves an externally supplied marker, records both `run_id`
and `example_run_id`, and flushes and shuts down Respan in `finally`.
