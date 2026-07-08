#!/usr/bin/env python3
"""Run the full Dify tracing example set in separate processes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "01_chat_blocking.py",
    "02_chat_streaming.py",
    "03_completion.py",
    "04_workflow_and_api.py",
    "05_respan_context_and_files.py",
]


def main() -> None:
    for script in SCRIPTS:
        print(f"\n### Running {script}")
        subprocess.run([sys.executable, script], cwd=EXAMPLE_DIR, check=True)


if __name__ == "__main__":
    main()
