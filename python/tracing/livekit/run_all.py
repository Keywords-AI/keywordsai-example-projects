from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES = [
    "01_llm_chat.py",
    "02_streaming_response.py",
    "03_tool_calling.py",
    "04_context_and_error.py",
    "05_live_openai.py",
]


def run() -> None:
    here = Path(__file__).resolve().parent
    for example in EXAMPLES:
        print(f"\n### running {example}", flush=True)
        subprocess.run([sys.executable, str(here / example)], check=True)


if __name__ == "__main__":
    run()
