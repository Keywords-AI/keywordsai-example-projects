"""Run all Hugging Face tracing examples in isolated Python processes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "01_text_generation_pipeline.py",
    "02_batch_prompts.py",
    "03_trace_content_disabled.py",
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
