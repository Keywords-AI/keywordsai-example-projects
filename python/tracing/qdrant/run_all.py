from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

EXAMPLES = (
    "01_sync_operations.py",
    "02_async_operations.py",
    "03_expected_error.py",
)


def main() -> int:
    root = Path(__file__).resolve().parent
    marker = os.getenv("RESPAN_EXAMPLE_RUN_ID") or (
        "otel2-qdrant-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    )
    env = {**os.environ, "RESPAN_EXAMPLE_RUN_ID": marker}
    timeout = float(os.getenv("RESPAN_EXAMPLE_TIMEOUT_SECONDS", "60"))
    failures: list[str] = []
    print(f"RESPAN_EXAMPLE_RUN_ID={marker}", flush=True)
    for example in EXAMPLES:
        print(f"\n### {example}", flush=True)
        try:
            completed = subprocess.run(
                [sys.executable, str(root / example)],
                cwd=root,
                env=env,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{example}: timeout")
            continue
        if completed.returncode:
            failures.append(f"{example}: exit {completed.returncode}")
    if failures:
        print("Failures: " + "; ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
