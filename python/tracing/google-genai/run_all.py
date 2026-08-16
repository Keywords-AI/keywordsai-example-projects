"""Run every Google GenAI tracing example with one audit marker."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

SCRIPTS = (
    "01_generate_content.py",
    "02_stream_content.py",
    "03_async_generate_content.py",
    "04_tool_calling.py",
)


def main() -> None:
    directory = Path(__file__).resolve().parent
    env = os.environ.copy()
    env.setdefault("RESPAN_EXAMPLE_RUN_ID", f"google-genai-{uuid4().hex[:10]}")
    print(f"RESPAN_EXAMPLE_RUN_ID={env['RESPAN_EXAMPLE_RUN_ID']}", flush=True)
    for script in SCRIPTS:
        subprocess.run([sys.executable, str(directory / script)], env=env, check=True)


if __name__ == "__main__":
    main()
