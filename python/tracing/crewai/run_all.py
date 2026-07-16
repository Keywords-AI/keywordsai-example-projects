"""Run all CrewAI tracing examples in isolated Python processes."""

from __future__ import annotations

from datetime import datetime, timezone
import os
import subprocess
import sys
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "01_basic_crew.py",
    "02_tool_use.py",
    "03_attributes.py",
]


def main() -> None:
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID") or datetime.now(timezone.utc).strftime(
        "crewai-%Y%m%d-%H%M%S"
    )
    env = os.environ.copy()
    env["RESPAN_EXAMPLE_RUN_ID"] = run_id

    print(f"CrewAI example run id: {run_id}", flush=True)
    for script in SCRIPTS:
        print(f"\n== Running {script} ==", flush=True)
        subprocess.run(
            [sys.executable, str(EXAMPLE_DIR / script)],
            cwd=EXAMPLE_DIR,
            env=env,
            check=True,
        )


if __name__ == "__main__":
    main()
