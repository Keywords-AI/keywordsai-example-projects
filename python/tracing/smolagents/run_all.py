"""Run every committed smolagents tracing example."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = (
    "01_code_agent.py",
    "02_tool_calling_agent.py",
    "03_expected_tool_failure.py",
    "04_streaming_agent.py",
)


def main() -> None:
    root = Path(__file__).resolve().parent
    env = os.environ.copy()
    env.setdefault(
        "RESPAN_EXAMPLE_RUN_ID",
        datetime.now(timezone.utc).strftime("otel2-smolagents-%Y%m%dT%H%M%SZ"),
    )
    failures: list[str] = []
    for script in SCRIPTS:
        try:
            result = subprocess.run(
                [sys.executable, str(root / script)],
                check=False,
                env=env,
                timeout=240,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{script}: timeout")
            continue
        if result.returncode:
            failures.append(f"{script}: exit {result.returncode}")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
