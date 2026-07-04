# Watson Orchestrate ADK tracing examples

These examples trace IBM watsonx Orchestrate ADK activity with Respan.

They load environment variables from `respan-example-projects/.env`.

Required for all scripts:

- `RESPAN_API_KEY`
- `RESPAN_BASE_URL` (optional, defaults to `https://api.respan.ai/api`)

Required for the live run-client script:

- `WATSON_ORCHESTRATE_BASE_URL`
- `WATSON_ORCHESTRATE_API_KEY`
- `WATSON_ORCHESTRATE_AGENT_ID`
- `WATSON_ORCHESTRATE_THREAD_ID` (optional)

Required for the live watsonx.ai chat script:

- `WATSONX_APIKEY`
- `WATSONX_SPACE_ID`
- `WATSONX_URL` (optional)
- `WATSON_ORCHESTRATE_LLM_MODEL` (optional)

Run from this directory after installing local packages:

```bash
python 01_local_agent_tool.py
python 02_live_run_client.py
python 03_live_watsonx_chat.py
```

`01_local_agent_tool.py` does not need IBM service credentials. It defines an
ADK tool and agent spec, invokes a successful tool, and invokes a deterministic
failing tool so the instrumentation emits both success and error tool spans.

`02_live_run_client.py` submits a message to a deployed Orchestrate agent when
the `WATSON_ORCHESTRATE_*` variables are set.

`03_live_watsonx_chat.py` calls the ADK watsonx.ai autodiscover chat client when
the `WATSONX_*` variables are set.
