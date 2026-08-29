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


def test_workflow_roots_accept_bounded_semantic_arguments() -> None:
    for path in EXAMPLE_DIR.glob("[0-9][0-9]_*.py"):
        tree = ast.parse(path.read_text())
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
        assert workflows
        assert all(function.args.args for function in workflows)


def test_env_loading_preserves_shell_values() -> None:
    source = (EXAMPLE_DIR / "_shared.py").read_text()
    assert "override=False" in source
