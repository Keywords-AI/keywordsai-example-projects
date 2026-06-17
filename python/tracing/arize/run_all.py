from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES = [
    "01_spans_and_ml.py",
    "02_datasets_projects_spaces.py",
    "03_experiments_prompts_evaluators.py",
    "04_admin_operations.py",
]


def run() -> None:
    here = Path(__file__).resolve().parent
    for example in EXAMPLES:
        print(f"\n### running {example}", flush=True)
        subprocess.run([sys.executable, str(here / example)], check=True)


if __name__ == "__main__":
    run()
