from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]

SCENARIOS = (
    ("outcomes", "scenarios/outcomes_case.py", 0, True),
    ("expected-failure", "scenarios/failure_case.py", 1, True),
    ("privacy", "scenarios/privacy_case.py", 1, False),
)


def main() -> int:
    load_dotenv(REPO_ROOT / ".env", override=False)
    marker = os.getenv("RESPAN_EXAMPLE_RUN_ID") or (
        "otel2-pytest-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    )
    timeout = float(os.getenv("RESPAN_EXAMPLE_TIMEOUT_SECONDS", "60"))
    failures: list[str] = []
    print(f"RESPAN_EXAMPLE_RUN_ID={marker}", flush=True)
    for name, scenario, expected_exit, capture_content in SCENARIOS:
        env = {
            **os.environ,
            "RESPAN_EXAMPLE_RUN_ID": marker,
            "RESPAN_PYTEST_WORKFLOW_NAME": f"pytest_{name}",
        }
        command = [
            sys.executable,
            "-m",
            "pytest",
            "--respan-tracing",
            "-q",
            str(ROOT / scenario),
        ]
        if not capture_content:
            command.insert(-2, "--no-respan-capture-content")
        print(f"\n### {name}", flush=True)
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=env,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{name}: timeout")
            continue
        if completed.returncode != expected_exit:
            failures.append(
                f"{name}: exit {completed.returncode}, expected {expected_exit}"
            )
    if failures:
        print("Failures: " + "; ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
