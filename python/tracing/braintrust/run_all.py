"""Run every Braintrust tracing example with one shared marker."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
EXAMPLES = (
    "01_basic_workflow.py",
    "02_nested_tool_workflow.py",
    "03_scored_evaluation_workflow.py",
)


def main() -> None:
    env = os.environ.copy()
    env.setdefault("RESPAN_EXAMPLE_RUN_ID", f"braintrust-{uuid.uuid4().hex[:10]}")
    failures: list[str] = []
    for example in EXAMPLES:
        print(f"\n=== {example} ===", flush=True)
        result = subprocess.run(
            [sys.executable, str(EXAMPLE_DIR / example)],
            cwd=EXAMPLE_DIR,
            env=env,
            check=False,
        )
        if result.returncode:
            failures.append(example)
    if failures:
        raise SystemExit(f"Braintrust examples failed: {', '.join(failures)}")
    print(f"RESPAN_EXAMPLE_RUN_ID={env['RESPAN_EXAMPLE_RUN_ID']}")


if __name__ == "__main__":
    main()
