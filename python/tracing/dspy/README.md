# DSPy + Respan Examples

Runnable examples showing native DSPy 3.x instrumentation with Respan through
`respan-instrumentation-dspy`. The examples use DSPy's own APIs rather than
templates copied from other frameworks.

## Setup

From the repository root, keep your existing `.env` with `RESPAN_API_KEY`. The
scripts load env files from this directory and the `respan-example-projects`
repo root automatically.

```bash
cd python/tracing/dspy
pip install -r requirements.txt
```

For local SDK development:

```bash
pip install -e /path/to/respan/python-sdks/respan-sdk \
            -e /path/to/respan/python-sdks/respan-tracing \
            -e /path/to/respan/python-sdks/respan \
            -e /path/to/respan/python-sdks/instrumentations/respan-instrumentation-dspy \
            dspy python-dotenv
```

## Examples

| File | DSPy API exercised |
|------|--------------------|
| `01_predict_signature.py` | `dspy.Signature` + `dspy.Predict` |
| `02_chain_of_thought.py` | `dspy.ChainOfThought` |
| `03_module_workflow.py` | Custom `dspy.Module` composed from predictors |
| `04_tool_call.py` | Direct `dspy.Tool` execution |
| `05_react_agent.py` | `dspy.ReAct` with a Python tool |
| `06_evaluate_program.py` | `dspy.Evaluate` on a small devset |

Each script sets distinct `app_name`, `example_name`, `example_run_id`,
`trace_group_identifier`, and `custom_identifier` values so exported results can
be traced back to the script that produced them. The root workflow span also
records a compact example input and output, while child spans contain the DSPy
module, adapter, LM, evaluation, and tool details.

Run any example:

```bash
python 01_predict_signature.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RESPAN_API_KEY` | Yes | Your Respan API key. Used for gateway calls and tracing. |
| `RESPAN_BASE_URL` | No | Defaults to `https://api.respan.ai/api`. |
| `RESPAN_DSPY_MODEL` | No | Defaults to `openai/gpt-4o-mini`. |
| `RESPAN_EXAMPLE_RUN_ID` | No | Override the generated run id for repeatable MCP filtering. |
