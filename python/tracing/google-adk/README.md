# Google ADK tracing examples

These examples run Google ADK agents through the Respan gateway and export ADK
runner, agent, LLM, and tool spans to Respan.

Each script wraps the run in a Respan workflow whose name matches the script
filename, so the platform result is easy to map back to the example.

The scripts load environment variables from the repo root `.env` file:

- `RESPAN_API_KEY`
- `RESPAN_BASE_URL`
- `RESPAN_GATEWAY_API_KEY`
- `RESPAN_GATEWAY_BASE_URL`
- `RESPAN_MODEL`

Run from this directory after installing local packages:

```bash
python 01_hello_world.py
python 02_tool_use.py
python 03_respan_attributes.py
```
