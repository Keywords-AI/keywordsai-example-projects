from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent
EXAMPLES = [
    "hello_world.py",
    "async_parallel.py",
    "attributes.py",
    "batch.py",
    "batch_async.py",
    "decorators.py",
    "multi_turn.py",
    "prompt.py",
    "prompt_multi_turn.py",
    "responses_hello_world.py",
    "responses_multi_turn.py",
    "responses_prompt.py",
    "responses_streaming.py",
    "responses_structured_output.py",
    "responses_tool_calls.py",
    "streaming.py",
    "structured_output.py",
    "tool_calls.py",
]


def marker() -> str:
    configured = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if configured:
        return configured
    return f"openai-sdk-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"


def main() -> int:
    shared_marker = marker()
    environment = os.environ.copy()
    environment["RESPAN_EXAMPLE_RUN_ID"] = shared_marker
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    failures: list[str] = []

    print(f"RESPAN_EXAMPLE_RUN_ID={shared_marker}", flush=True)
    for index, script_name in enumerate(EXAMPLES, start=1):
        print(f"[{index:02d}/{len(EXAMPLES):02d}] {script_name}", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, str(EXAMPLE_DIR / script_name)],
                cwd=EXAMPLE_DIR,
                env=environment,
                check=False,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{script_name}:timeout")
            continue
        if result.returncode:
            failures.append(f"{script_name}:{result.returncode}")

    print(f"completed={len(EXAMPLES) - len(failures)}/{len(EXAMPLES)}", flush=True)
    if failures:
        print(f"failures={','.join(failures)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
