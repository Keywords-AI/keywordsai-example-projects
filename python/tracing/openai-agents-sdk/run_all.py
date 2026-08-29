"""Run every collected and legacy direct OpenAI Agents example with one marker."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(find_dotenv(), override=False)
DEFAULT_COMMAND_TIMEOUT_SECONDS = 300


def _marker() -> str:
    existing = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if existing:
        return existing
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"otel2-openai-agents-{timestamp}"


def _timeout_seconds() -> int:
    raw = os.getenv("RESPAN_EXAMPLE_COMMAND_TIMEOUT_SECONDS", "")
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_COMMAND_TIMEOUT_SECONDS
    return value if value > 0 else DEFAULT_COMMAND_TIMEOUT_SECONDS


def _run_commands(
    commands: list[list[str]], *, env: dict[str, str], timeout_seconds: int
) -> list[tuple[list[str], str]]:
    failures: list[tuple[list[str], str]] = []
    for index, command in enumerate(commands, start=1):
        print(f"[{index}/{len(commands)}] {' '.join(command)}", flush=True)
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=env,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            detail = f"timeout after {timeout_seconds}s"
            print(detail, flush=True)
            failures.append((command, detail))
            continue
        print(f"exit={completed.returncode}", flush=True)
        if completed.returncode:
            failures.append((command, f"exit={completed.returncode}"))
    return failures


def main() -> int:
    marker = _marker()
    env = {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "RESPAN_EXAMPLE_RUN_ID": marker,
    }
    commands = [
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        [sys.executable, "handoffs/message_filter_test.py"],
        [sys.executable, "handoffs/message_filter_streaming_test.py"],
        [sys.executable, "complex_edge_cases_test.py"],
    ]
    print(f"RESPAN_EXAMPLE_RUN_ID={marker}", flush=True)
    failures = _run_commands(commands, env=env, timeout_seconds=_timeout_seconds())
    if failures:
        print("OpenAI Agents example failures:", flush=True)
        for command, detail in failures:
            print(f"  {detail}: {' '.join(command)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
