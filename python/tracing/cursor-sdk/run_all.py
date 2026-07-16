from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES = [
    "01_agent_turn.py",
    "02_terminal_and_mcp_tools.py",
    "03_stop_cleanup.py",
    "04_full_hook_transcript.py",
]


def main() -> None:
    here = Path(__file__).resolve().parent
    for example in EXAMPLES:
        print(f"\n### running {example}", flush=True)
        subprocess.run([sys.executable, str(here / example)], check=True)


if __name__ == "__main__":
    main()
