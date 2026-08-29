from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_examples_use_semantic_workflow_inputs_and_nested_teardown() -> None:
    for path in sorted(ROOT.glob("0*.py")):
        source = path.read_text(encoding="utf-8")
        ast.parse(source)
        assert "@workflow" in source
        assert "client.close()" in source
        assert "finally:" in source
        assert "finish_respan(respan)" in source
        assert "api_key" not in source


def test_shared_marker_and_metadata_contract() -> None:
    source = (ROOT / "_shared.py").read_text(encoding="utf-8")
    assert "override=False" in source
    assert '"example_run_id": marker' in source
    assert '"run_id": marker' in source
    assert '"example_set": "qdrant"' in source


def test_runner_uses_one_marker_and_continues_after_failures() -> None:
    source = (ROOT / "run_all.py").read_text(encoding="utf-8")
    assert "RESPAN_EXAMPLE_RUN_ID" in source
    assert "check=False" in source
    assert "TimeoutExpired" in source
