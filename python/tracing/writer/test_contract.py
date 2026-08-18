from __future__ import annotations

import ast
from pathlib import Path

HERE = Path(__file__).resolve().parent


def test_all_workflows_have_semantic_arguments_and_nested_teardown() -> None:
    for path in sorted(HERE.glob("[0-9][0-9]_*.py")):
        source = path.read_text()
        tree = ast.parse(source)
        workflows = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(
                isinstance(decorator, ast.Call)
                and getattr(decorator.func, "id", "") == "workflow"
                for decorator in node.decorator_list
            )
        ]
        assert workflows
        assert all(workflow.args.args for workflow in workflows)
        assert "finish_respan(respan)" in source
        assert (
            "close_client(client)" in source or "close_async_client(client)" in source
        )


def test_exact_marker_and_deterministic_default() -> None:
    shared = (HERE / "_shared.py").read_text()
    assert "override=False" in shared
    assert 'os.getenv("RESPAN_EXAMPLE_RUN_ID")' in shared
    assert '"example_run_id": example_run_id()' in shared
    assert '"run_id": example_run_id()' in shared
    assert 'return mode not in {"live", "real"}' in shared


def test_runner_aggregates_failures_and_timeouts() -> None:
    source = (HERE / "run_all.py").read_text()
    assert "check=False" in source
    assert "timeout=120" in source
    assert "failures.append" in source


def test_tool_example_has_connected_execution_and_follow_up() -> None:
    source = (HERE / "03_tool_calling.py").read_text()
    assert '@tool(name="get_weather")' in source
    assert "tool_result = get_weather(**arguments)" in source
    assert "follow_up = _CLIENT.chat.chat" in source
