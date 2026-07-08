from __future__ import annotations

import runpy
from pathlib import Path

EXAMPLES = [
    "01_run_prediction.py",
    "02_stream_prediction.py",
    "03_async_run_prediction.py",
    "04_prediction_lifecycle.py",
]


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    for script in EXAMPLES:
        print(f"\n=== {script} ===", flush=True)
        runpy.run_path(str(base_dir / script), run_name="__main__")


if __name__ == "__main__":
    main()
