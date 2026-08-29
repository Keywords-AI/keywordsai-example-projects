from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_every_example_has_finally_shutdown_and_semantic_prompt() -> None:
    for path in sorted(ROOT.glob("0*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert "finally:" in source
        assert "finish_respan(respan)" in source
        assert any(
            isinstance(node, ast.Constant) and isinstance(node.value, str)
            for node in ast.walk(tree)
        )


def test_runner_uses_one_marker_and_continues_after_failures() -> None:
    source = (ROOT / "run_all.py").read_text(encoding="utf-8")
    assert "RESPAN_EXAMPLE_RUN_ID" in source
    assert "check=False" in source
    assert "TimeoutExpired" in source


def test_dotenv_does_not_override_shell_marker() -> None:
    source = (ROOT / "_gateway.py").read_text(encoding="utf-8")
    assert "override=False" in source
    assert '"example_run_id": marker' in source
    assert '"run_id": marker' in source
    assert 'os.getenv("RESPAN_PYDANTIC_LIVE"' in source
    assert "TestModel" in source
    assert 'TestModel(model_name="test")' in source
