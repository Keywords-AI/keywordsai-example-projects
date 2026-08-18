from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = ["01_modern_metrics.py", "02_evaluate.py", "03_experiment.py"]
TIMEOUT_SECONDS = 120


def marker() -> str:
    existing = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if existing:
        return existing
    return f"otel2-ragas-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"


def main() -> None:
    env = dict(os.environ)
    env["RESPAN_EXAMPLE_RUN_ID"] = marker()
    failures: list[str] = []
    print(f"RESPAN_EXAMPLE_RUN_ID={env['RESPAN_EXAMPLE_RUN_ID']}", flush=True)
    for script in SCRIPTS:
        try:
            result = subprocess.run(
                [sys.executable, str(EXAMPLE_DIR / script)],
                cwd=EXAMPLE_DIR,
                env=env,
                timeout=TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{script}: timed out")
            continue
        if result.returncode:
            failures.append(f"{script}: exit {result.returncode}")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
