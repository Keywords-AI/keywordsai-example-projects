from __future__ import annotations

import ast
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent


def test_runner_covers_all_examples_and_aggregates_failures() -> None:
    source = (EXAMPLE_DIR / "run_all.py").read_text()
    tree = ast.parse(source)
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "EXAMPLES"
            for target in node.targets
        )
    )
    assert ast.literal_eval(assignment.value) == sorted(
        path.name for path in EXAMPLE_DIR.glob("[0-9][0-9]_*.py")
    )
    assert "TimeoutExpired" in source
    assert "failures" in source


def test_workflows_accept_semantic_values_not_clients() -> None:
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
        for function in workflows:
            names = [argument.arg for argument in function.args.args]
            assert names
            assert "client" not in names


def test_marker_and_live_mode_are_explicit() -> None:
    shared = (EXAMPLE_DIR / "_shared.py").read_text()
    assert "override=False" in shared
    assert "example_run_id" in shared
    assert "RESPAN_REPLICATE_LIVE" in shared
