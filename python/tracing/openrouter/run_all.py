from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES = [
    "01_chat_completion.py",
    "02_streaming_chat.py",
    "03_tool_calling.py",
    "04_async_chat.py",
    "05_structured_output.py",
]


def run() -> None:
    here = Path(__file__).resolve().parent
    for example in EXAMPLES:
        print("\n### running " + example, flush=True)
        subprocess.run([sys.executable, str(here / example)], check=True)


if __name__ == "__main__":
    run()
