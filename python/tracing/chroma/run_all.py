from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "01_collection_lifecycle.py",
    "02_write_and_read.py",
    "03_query_and_filters.py",
    "04_update_upsert_delete.py",
    "05_propagated_attributes.py",
]


def main() -> None:
    for script in SCRIPTS:
        print(f"\n### Running {script}")
        subprocess.run([sys.executable, str(EXAMPLE_DIR / script)], check=True)


if __name__ == "__main__":
    main()
