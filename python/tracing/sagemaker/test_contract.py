from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = tuple(sorted(ROOT.glob("0[1-4]_*.py")))


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_marker_precedence_and_shared_runner_contract() -> None:
    shared = _source(ROOT / "_shared.py")
    runner = _source(ROOT / "run_all.py")
    assert "override=False" in shared
    assert 'os.getenv("RESPAN_EXAMPLE_RUN_ID")' in shared
    assert "env.setdefault" in runner
    assert "subprocess.TimeoutExpired" in runner
    assert "check=False" in runner
    assert all(path.name in runner for path in SCRIPTS)


def test_workflows_capture_only_bounded_semantic_arguments() -> None:
    for path in SCRIPTS:
        tree = ast.parse(_source(path))
        workflows = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            and any(
                isinstance(decorator, ast.Call)
                and getattr(decorator.func, "id", None) == "workflow"
                for decorator in node.decorator_list
            )
        ]
        assert len(workflows) == 1
        names = [argument.arg for argument in workflows[0].args.args]
        assert names and not {"client", "sdk", "dsn"}.intersection(names)
        source = _source(path)
        assert "client.close()" in source
        assert "respan.shutdown()" in source


def test_documentation_is_portable() -> None:
    readme = _source(ROOT / "README.md")
    requirements = _source(ROOT / "requirements.txt")
    assert "/home/" not in readme
    assert "/Users/" not in readme
    assert " -e " not in requirements
