from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES = [
    "01_chat_completion.py",
    "02_streaming_chat.py",
    "03_tool_calling.py",
    "04_text_completion.py",
    "05_async_chat.py",
    "06_graph_question.py",
    "07_application_generation.py",
    "08_vision_translation_tools.py",
    "09_structured_parse.py",
]


def run() -> None:
    here = Path(__file__).resolve().parent
    for example in EXAMPLES:
        print(f"\n### running {example}", flush=True)
        subprocess.run([sys.executable, str(here / example)], check=True)


if __name__ == "__main__":
    run()
