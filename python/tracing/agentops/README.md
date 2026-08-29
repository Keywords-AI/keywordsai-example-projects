# AgentOps tracing

These deterministic examples exercise AgentOps' workflow, agent, task, and
tool decorators through the Respan instrumentation, including a caught failed
task span.

Install the requirements, link `respan-instrumentation-agentops` from the local
Respan checkout for development, and run both scripts from this directory:

```bash
python 01_decorator_hierarchy.py
python 02_expected_failure.py
```

The examples load `../../../.env`, honor `RESPAN_EXAMPLE_RUN_ID`, and always
shut down Respan so short-lived processes flush their spans.
