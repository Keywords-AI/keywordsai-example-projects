from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES = [
    "01_chat.py",
    "02_completion.py",
    "03_embeddings.py",
    "04_async_streaming.py",
    "05_evaluate_explain.py",
]


def main() -> None:
    root = Path(__file__).resolve().parent
    for script in EXAMPLES:
        print(f"\n--- running {script} ---", flush=True)
        subprocess.run([sys.executable, str(root / script)], check=True)


if __name__ == "__main__":
    main()
