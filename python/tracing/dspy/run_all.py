#!/usr/bin/env python3
"""Run the full DSPy tracing example set in separate processes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "01_predict_signature.py",
    "02_chain_of_thought.py",
    "03_module_workflow.py",
    "04_tool_call.py",
    "05_react_agent.py",
    "06_evaluate_program.py",
]


def main() -> None:
    for script in SCRIPTS:
        print(f"\n### Running {script}", flush=True)
        subprocess.run([sys.executable, script], cwd=EXAMPLE_DIR, check=True)


if __name__ == "__main__":
    main()
