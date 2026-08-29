from __future__ import annotations

import subprocess
import sys
from pathlib import Path


EXAMPLES = [
    "01_assistant_run.py",
    "02_tool_use.py",
    "03_round_robin_team.py",
]


def run() -> None:
    here = Path(__file__).resolve().parent
    failures: list[str] = []
    for example in EXAMPLES:
        print(f"\n### running {example}", flush=True)
        result = subprocess.run([sys.executable, str(here / example)], check=False)
        if result.returncode:
            failures.append(f"{example} (exit {result.returncode})")
    if failures:
        raise SystemExit(f"AutoGen example failures: {', '.join(failures)}")


if __name__ == "__main__":
    run()
