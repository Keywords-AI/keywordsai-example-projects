from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = (
    "01_offline_pipeline.py",
    "02_gateway_llm_pipeline.py",
    "03_expected_error.py",
)
DEFAULT_TIMEOUT_SECONDS = 120.0


def main() -> None:
    run_marker = os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip() or (
        "pipecat-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    timeout = float(
        os.getenv("RESPAN_EXAMPLE_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
    )
    env = os.environ.copy()
    env["RESPAN_EXAMPLE_RUN_ID"] = run_marker
    failures: list[str] = []
    for script in SCRIPTS:
        print(f"\n### Running {script}", flush=True)
        try:
            completed = subprocess.run(
                [sys.executable, str(EXAMPLE_DIR / script)],
                check=False,
                env=env,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{script}: timed out after {timeout:g}s")
            continue
        if completed.returncode:
            failures.append(f"{script}: exited {completed.returncode}")
    if failures:
        raise SystemExit("Pipecat example failures:\n- " + "\n- ".join(failures))
    print(f"\nCompleted Pipecat examples: RESPAN_EXAMPLE_RUN_ID={run_marker}")


if __name__ == "__main__":
    main()
