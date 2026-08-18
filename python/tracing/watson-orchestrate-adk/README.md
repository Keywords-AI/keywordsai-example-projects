# Watson Orchestrate ADK OTel 2.x examples

The first five scripts exercise the installed
`ibm-watsonx-orchestrate` 2.15 public classes without service credentials:
local Python tools, synchronous and asynchronous run clients, chat, and a
precise provider 429. Deterministic methods are installed on the real current
SDK classes before Respan activation and restored after shutdown.

`06_live_run_client.py` and `07_live_watsonx_chat.py` call IBM services only
when their documented credentials are present; otherwise they exit with an
explicit skip.

Every deterministic trace retains the exact caller-supplied
`RESPAN_EXAMPLE_RUN_ID` in both `run_id` and `example_run_id` metadata.

```bash
RESPAN_EXAMPLE_RUN_ID=my-exact-marker python run_all.py
```

The runner applies one marker and timeout to every process, continues through
failures, and returns nonzero if any example fails.
