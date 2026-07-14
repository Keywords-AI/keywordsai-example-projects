from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = ["01_upsert_and_query.py"]


def main() -> None:
    for script in SCRIPTS:
        print(f"\n### Running {script}")
        subprocess.run([sys.executable, str(EXAMPLE_DIR / script)], check=True)


if __name__ == "__main__":
    main()
