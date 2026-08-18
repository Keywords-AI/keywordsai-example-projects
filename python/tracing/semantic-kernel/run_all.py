"""Run every committed Semantic Kernel tracing example."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = (
    "01_kernel_function.py",
    "02_chat_completion.py",
    "03_plugin_tool_call.py",
    "04_function_failure.py",
)


def main() -> None:
    root = Path(__file__).resolve().parent
    env = os.environ.copy()
    env.setdefault(
        "RESPAN_EXAMPLE_RUN_ID",
        datetime.now(timezone.utc).strftime("otel2-semantic-kernel-%Y%m%dT%H%M%SZ"),
    )
    failures: list[str] = []
    for script in SCRIPTS:
        try:
            result = subprocess.run(
                [sys.executable, str(root / script)],
                check=False,
                env=env,
                timeout=180,
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
