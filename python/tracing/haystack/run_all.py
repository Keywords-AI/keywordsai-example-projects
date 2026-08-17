"""Run every committed Haystack tracing scenario in an isolated process."""

from __future__ import annotations

import os
import subprocess
import sys
from importlib import import_module
from pathlib import Path


def main() -> None:
    directory = Path(__file__).resolve().parent
    managed_prompt_names = {
        "43_prompt_management_gateway.py",
        "44_prompt_management_extra_body_gateway.py",
    }
    scripts = [
        script
        for script in sorted(directory.glob("[0-9][0-9]_*.py"))
        if script.name not in managed_prompt_names
    ]
    for script in scripts:
        print(f"\n== running {script.name} ==", flush=True)
        subprocess.run([sys.executable, str(script)], cwd=directory, check=True)

    print("\n== running 44_prompt_management_extra_body_gateway.py ==", flush=True)
    bootstrap = import_module("44_prompt_management_extra_body_gateway")
    bootstrap_result = bootstrap.run_prompt_management_extra_body_gateway_example()
    managed_prompt_id = str(bootstrap_result["managed_prompt_id"])

    print("\n== running 43_prompt_management_gateway.py ==", flush=True)
    managed_prompt_environment = os.environ.copy()
    managed_prompt_environment["RESPAN_PROMPT_ID"] = managed_prompt_id
    subprocess.run(
        [sys.executable, str(directory / "43_prompt_management_gateway.py")],
        cwd=directory,
        check=True,
        env=managed_prompt_environment,
    )

    print("\n== running complex_edge_cases.py ==", flush=True)
    subprocess.run(
        [sys.executable, str(directory / "complex_edge_cases.py")],
        cwd=directory,
        check=True,
    )


if __name__ == "__main__":
    main()
