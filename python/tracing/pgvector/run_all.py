from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = (
    "01_sync_similarity.py",
    "02_async_similarity.py",
    "03_bulk_server_cursor_failure.py",
    "04_live_postgres.py",
)
DEFAULT_TIMEOUT_SECONDS = 60.0


def main() -> None:
    marker = os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip() or (
        "pgvector-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    timeout = float(
        os.getenv("RESPAN_EXAMPLE_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
    )
    env = os.environ.copy()
    env["RESPAN_EXAMPLE_RUN_ID"] = marker
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
        raise SystemExit("PGVector example failures:\n- " + "\n- ".join(failures))
    print(f"\nCompleted PGVector example set: RESPAN_EXAMPLE_RUN_ID={marker}")


if __name__ == "__main__":
    main()
