from __future__ import annotations

import subprocess
import sys
from pathlib import Path


EXAMPLES = [
    "01_invoke_model.py",
    "02_converse.py",
    "03_converse_stream.py",
    "04_converse_tool.py",
    "05_converse_error.py",
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
        raise SystemExit(f"AWS Bedrock example failures: {', '.join(failures)}")


if __name__ == "__main__":
    run()
