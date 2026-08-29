"""Run all Claude Agent SDK tracing examples in isolated processes."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


EXAMPLE_DIR = Path(__file__).resolve().parent
EXAMPLES = [
    "01_hello_world.py",
    "02_wrapped_query.py",
    "03_multi_turn.py",
    "04_stream_messages.py",
    "05_tool_use.py",
    "06_multi_tool.py",
]


def main() -> None:
    run_id = os.environ["RESPAN_EXAMPLE_RUN_ID"]
    print(f"Claude Agent SDK example run id: {run_id}", flush=True)
    for example in EXAMPLES:
        print(f"\n=== {example} ===", flush=True)
        subprocess.run(
            [sys.executable, str(EXAMPLE_DIR / example)],
            cwd=EXAMPLE_DIR,
            env=os.environ.copy(),
            check=True,
        )


if __name__ == "__main__":
    main()
