# Restate tracing examples

These examples register real Restate 1.x workflow and service handlers and
exercise their configured invocation context managers with a deterministic
in-process invocation fixture. This validates instrumentation mapping without
requiring a deployed Restate runtime or protocol VM.

A true replay/deployment validation still requires an external Restate server;
that service boundary is intentionally not replaced by package behavior.

```bash
RESPAN_EXAMPLE_RUN_ID=otel2-restate-check python run_all.py
```

The runner preserves the supplied marker, times out each child independently,
continues after failures, and exits nonzero if any example fails.
