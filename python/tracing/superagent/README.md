# Superagent Tracing Examples

These examples trace the Superagent `safety-agent` SDK with
`respan-instrumentation-superagent`.

Each script wraps the run in a Respan workflow whose name matches the script
filename, so the platform result is easy to map back to the example.

## Setup

Run from this directory after installing local packages:

```bash
pip install -r requirements.txt
python 01_guard.py
python 02_redact.py
python 03_workflow.py
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
