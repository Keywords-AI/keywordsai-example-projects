from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_runner_preserves_one_marker_and_aggregates_results() -> None:
    source = (ROOT / "run_all.py").read_text(encoding="utf-8")
    assert "override=False" in source
    assert "RESPAN_EXAMPLE_RUN_ID" in source
    assert "check=False" in source
    assert "TimeoutExpired" in source
    assert source.count("RESPAN_PYTEST_WORKFLOW_NAME") == 1


def test_scenario_files_are_bounded_and_parse() -> None:
    for path in sorted((ROOT / "scenarios").glob("*_case.py")):
        source = path.read_text(encoding="utf-8")
        ast.parse(source)
        assert len(source.encode("utf-8")) < 4_000


def test_privacy_scenario_uses_capture_disabled() -> None:
    runner = (ROOT / "run_all.py").read_text(encoding="utf-8")
    assert "--no-respan-capture-content" in runner
    assert "pytest-secret-must-not-export" in (
        ROOT / "scenarios/privacy_case.py"
    ).read_text(encoding="utf-8")
