"""Run all maintained Instructor examples in isolated processes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "01_create.py",
    "02_validation_hooks.py",
    "03_create_with_completion.py",
    "04_create_iterable.py",
    "05_async_create.py",
]


def main() -> None:
    for script in SCRIPTS:
        print(f"\n== Running {script} ==", flush=True)
        subprocess.run(
            [sys.executable, str(EXAMPLE_DIR / script)],
            cwd=EXAMPLE_DIR,
            check=True,
        )


if __name__ == "__main__":
    main()
