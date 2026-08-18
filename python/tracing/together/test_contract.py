from __future__ import annotations

import ast
from pathlib import Path

from _shared import (
    example_attributes,
    load_root_env,
    make_custom_identifier,
)
from run_all import SCRIPTS

EXAMPLE_DIR = Path(__file__).resolve().parent


def test_shell_marker_survives_dotenv_and_propagation(monkeypatch) -> None:
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "shell-exact-marker")
    load_root_env()
    assert make_custom_identifier("contract") == "shell-exact-marker"
    with example_attributes("contract") as marker:
        assert marker == "shell-exact-marker"


def test_runner_covers_every_committed_numbered_example() -> None:
    expected = tuple(sorted(EXAMPLE_DIR.glob("[0-9][0-9]_*.py")))
    assert SCRIPTS == expected
    assert len(SCRIPTS) == 9


def test_workflow_roots_take_bounded_semantic_arguments() -> None:
    for script in SCRIPTS:
        tree = ast.parse(script.read_text())
        workflows = [
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(
                isinstance(decorator, ast.Call)
                and getattr(decorator.func, "id", None) == "workflow"
                for decorator in node.decorator_list
            )
        ]
        assert workflows, script.name
        for workflow in workflows:
            names = [argument.arg for argument in workflow.args.args]
            assert names
            assert all(
                blocked not in name.lower()
                for name in names
                for blocked in ("client", "key", "credential", "token")
            )


def test_requirements_are_registry_only() -> None:
    requirements = (EXAMPLE_DIR / "requirements.txt").read_text()
    assert "-e " not in requirements
    assert "file:" not in requirements
    assert "../../../../" not in requirements
