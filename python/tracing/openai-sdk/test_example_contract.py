from __future__ import annotations

import ast
import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

EXAMPLE_DIR = Path(__file__).resolve().parent
PUBLIC_EXAMPLES = {
    path.name
    for path in EXAMPLE_DIR.glob("*.py")
    if not path.name.startswith("_")
    and path.name not in {"run_all.py", "test_example_contract.py"}
}
CLIENT_EXAMPLES = {
    path.name
    for path in EXAMPLE_DIR.glob("*.py")
    if path.name in PUBLIC_EXAMPLES
    and (
        "make_sync_client" in path.read_text()
        or "make_async_client" in path.read_text()
    )
}


def _load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "openai_example_runner", EXAMPLE_DIR / "run_all.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_all_lists_every_public_example_once() -> None:
    module = ast.parse((EXAMPLE_DIR / "run_all.py").read_text())
    assignment = next(
        node
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "EXAMPLES"
            for target in node.targets
        )
    )
    listed = ast.literal_eval(assignment.value)
    assert len(listed) == 18
    assert len(set(listed)) == len(listed)
    assert set(listed) == PUBLIC_EXAMPLES


def test_shared_loader_preserves_shell_marker() -> None:
    source = (EXAMPLE_DIR / "_shared.py").read_text()
    assert "override=False" in source
    assert 'os.getenv("RESPAN_EXAMPLE_RUN_ID")' in source
    assert '"example_run_id": marker' in source


def test_every_example_has_explicit_shutdown() -> None:
    for script_name in PUBLIC_EXAMPLES:
        source = (EXAMPLE_DIR / script_name).read_text()
        assert "finish_respan(respan)" in source, script_name


def _contains_call(nodes: list[ast.stmt], name: str) -> bool:
    for node in nodes:
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            if isinstance(child.func, ast.Name) and child.func.id == name:
                return True
            if isinstance(child.func, ast.Attribute) and child.func.attr == name:
                return True
    return False


def test_client_examples_always_close_before_respan_shutdown() -> None:
    for script_name in CLIENT_EXAMPLES:
        module = ast.parse((EXAMPLE_DIR / script_name).read_text())
        scope = module.body
        if script_name == "async_parallel.py":
            main = next(
                node
                for node in module.body
                if isinstance(node, ast.AsyncFunctionDef) and node.name == "main"
            )
            scope = main.body

        outer = next(node for node in scope if isinstance(node, ast.Try))
        client_assignment = next(
            node
            for node in outer.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "client"
                for target in node.targets
            )
        )
        assert isinstance(client_assignment.value, ast.Call), script_name
        assert isinstance(client_assignment.value.func, ast.Name), script_name
        assert client_assignment.value.func.id in {
            "make_sync_client",
            "make_async_client",
        }, script_name

        nested = next(node for node in outer.body if isinstance(node, ast.Try))
        assert _contains_call(nested.finalbody, "close"), script_name
        assert _contains_call(outer.finalbody, "finish_respan"), script_name


def test_run_all_records_timeout_and_continues(monkeypatch, capsys) -> None:
    runner = _load_runner()
    runner.EXAMPLES = ["first.py", "second.py"]
    calls: list[str] = []

    def fake_run(command, **kwargs):
        del kwargs
        script = Path(command[-1]).name
        calls.append(script)
        if script == "first.py":
            raise subprocess.TimeoutExpired(command, 120)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    assert runner.main() == 1
    assert calls == ["first.py", "second.py"]
    output = capsys.readouterr().out
    assert "completed=1/2" in output
    assert "failures=first.py:timeout" in output


def test_run_all_disables_child_bytecode_caches(monkeypatch) -> None:
    runner = _load_runner()
    runner.EXAMPLES = ["example.py"]
    captured_environment: dict[str, str] = {}

    def fake_run(command, **kwargs):
        del command
        captured_environment.update(kwargs["env"])
        return subprocess.CompletedProcess([], 0)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    assert runner.main() == 0
    assert captured_environment["PYTHONDONTWRITEBYTECODE"] == "1"
