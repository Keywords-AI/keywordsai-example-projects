from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "01_invoke_endpoint_text.py",
    "02_invoke_endpoint_chat_tools.py",
    "03_invoke_endpoint_stream.py",
    "04_invoke_endpoint_async.py",
]


def main() -> None:
    root = Path(__file__).resolve().parent
    for script in SCRIPTS:
        print(f"\n=== {script} ===", flush=True)
        subprocess.run([sys.executable, str(root / script)], check=True)


if __name__ == "__main__":
    main()
