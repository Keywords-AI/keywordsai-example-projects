from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

EXAMPLES = [
    "01_text_generation.py",
    "02_streaming.py",
    "03_chat_tool_calling.py",
    "04_async_model_calls.py",
    "05_embeddings.py",
    "06_expected_error.py",
]


def run() -> None:
    here = Path(__file__).resolve().parent
    env = os.environ.copy()
    marker = env.get("RESPAN_EXAMPLE_RUN_ID") or "watsonx-local-run"
    env["RESPAN_EXAMPLE_RUN_ID"] = marker
    failures: list[str] = []
    for example in EXAMPLES:
        try:
            completed = subprocess.run(
                [sys.executable, str(here / example)],
                check=False,
                env=env,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{example}: timeout")
            continue
        if completed.returncode:
            failures.append(f"{example}: exit {completed.returncode}")
    if failures:
        raise RuntimeError("; ".join(failures))
    print(f"marker={marker}")


if __name__ == "__main__":
    run()
