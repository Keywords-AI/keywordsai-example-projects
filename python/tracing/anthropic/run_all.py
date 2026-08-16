"""Run the complete dedicated Python Anthropic example set."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES = (
    "01_basic.py",
    "02_streaming.py",
    "03_tool_round.py",
    "04_expected_error.py",
)


def main() -> None:
    root = Path(__file__).resolve().parent
    for script in EXAMPLES:
        print(f"\n--- running {script} ---", flush=True)
        subprocess.run([sys.executable, str(root / script)], check=True)


if __name__ == "__main__":
    main()
