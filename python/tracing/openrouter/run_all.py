from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXAMPLES = [
    "01_chat_completion.py",
    "02_streaming_chat.py",
    "03_tool_calling.py",
    "04_async_chat.py",
    "05_structured_output.py",
    "06_async_streaming_chat.py",
    "07_expected_error.py",
    "08_live_provider.py",
]

EXAMPLE_TIMEOUT_SECONDS = 90


def run() -> None:
    here = Path(__file__).resolve().parent
    marker = os.getenv("RESPAN_EXAMPLE_RUN_ID") or (
        "otel2-openrouter-local-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    child_env = dict(os.environ)
    child_env["RESPAN_EXAMPLE_RUN_ID"] = marker
    print(f"OpenRouter example marker: {marker}", flush=True)
    failures: list[str] = []
    for example in EXAMPLES:
        print("\n### running " + example, flush=True)
        try:
            result = subprocess.run(
                [sys.executable, str(here / example)],
                check=False,
                env=child_env,
                timeout=EXAMPLE_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{example}: timeout after {EXAMPLE_TIMEOUT_SECONDS}s")
            continue
        if result.returncode != 0:
            failures.append(f"{example}: exit {result.returncode}")

    if failures:
        details = "\n".join(f"- {failure}" for failure in failures)
        raise RuntimeError(f"OpenRouter example failures:\n{details}")


if __name__ == "__main__":
    run()
