from __future__ import annotations

import ast
from pathlib import Path

HERE = Path(__file__).resolve().parent


def test_all_examples_use_semantic_workflow_arguments_and_shutdown() -> None:
    for path in sorted(HERE.glob("0[1-6]_*.py")):
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
        assert "respan.shutdown()" in source


def test_marker_and_env_contract() -> None:
    shared = (HERE / "_shared.py").read_text()
    runner = (HERE / "run_all.py").read_text()
    assert "override=False" in shared
    assert 'os.getenv("RESPAN_EXAMPLE_RUN_ID")' in shared
    assert '"example_run_id": example_run_id()' in shared
    assert '"run_id": example_run_id()' in shared
    assert "timeout=120" in runner
    assert "check=False" in runner


def test_tool_example_executes_connected_tool_and_follow_up() -> None:
    source = (HERE / "03_chat_tool_calling.py").read_text()
    assert '@tool(name="get_weather")' in source
    assert "result = get_weather(**arguments)" in source
    assert "follow_up = _MODEL.chat" in source
