from __future__ import annotations

import ast
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent


def test_runner_covers_every_numbered_example() -> None:
    tree = ast.parse((EXAMPLE_DIR / "run_all.py").read_text())
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "SCRIPTS"
            for target in node.targets
        )
    )
    assert ast.literal_eval(assignment.value) == sorted(
        path.name for path in EXAMPLE_DIR.glob("[0-9][0-9]_*.py")
    )


def test_workflow_roots_accept_semantic_values() -> None:
    for path in EXAMPLE_DIR.glob("[0-9][0-9]_*.py"):
        tree = ast.parse(path.read_text())
        roots = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            and any(
                isinstance(decorator, ast.Call)
                and getattr(decorator.func, "id", None) == "workflow"
                for decorator in node.decorator_list
            )
        ]
        assert roots
        assert all(root.args.args for root in roots)


def test_marker_and_teardown_contracts() -> None:
    shared = (EXAMPLE_DIR / "_shared.py").read_text()
    assert "override=False" in shared
    assert "example_run_id" in shared
    assert "respan.flush()" in shared
    assert "respan.shutdown()" in shared
