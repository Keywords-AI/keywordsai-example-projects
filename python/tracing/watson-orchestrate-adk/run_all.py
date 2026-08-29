from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = tuple(sorted(EXAMPLE_DIR.glob("[0-9][0-9]_*.py")))
TIMEOUT_SECONDS = int(os.getenv("RESPAN_EXAMPLE_TIMEOUT_SECONDS", "90"))


def main() -> int:
    marker = os.getenv("RESPAN_EXAMPLE_RUN_ID") or (
        f"otel2-watson-orchestrate-{uuid4().hex[:12]}"
    )
    environment = dict(os.environ)
    environment["RESPAN_EXAMPLE_RUN_ID"] = marker
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    failures: list[str] = []
    print(f"marker={marker} scripts={len(SCRIPTS)}", flush=True)
    for script in SCRIPTS:
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=EXAMPLE_DIR,
                env=environment,
                check=False,
                timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{script.name}:timeout")
            continue
        if result.returncode:
            failures.append(f"{script.name}:exit={result.returncode}")
    if failures:
        print("failures=" + ",".join(failures), flush=True)
        return 1
    print(f"completed={len(SCRIPTS)} marker={marker}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
