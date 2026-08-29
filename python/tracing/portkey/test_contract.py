from __future__ import annotations

import ast
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import _shared
import pytest
import run_all

EXAMPLE_DIR = Path(__file__).resolve().parent


def _signatures(filename: str) -> list[list[str]]:
    module = ast.parse((EXAMPLE_DIR / filename).read_text())
    return [
        [argument.arg for argument in node.args.args]
        for node in ast.walk(module)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Name)
            and decorator.func.id == "workflow"
            for decorator in node.decorator_list
        )
    ]


def test_roots_accept_only_semantic_inputs():
    for script in run_all.SCRIPTS:
        assert _signatures(script) == [["prompt"]] or (
            script == "04_tool_calling.py" and _signatures(script) == [["city"]]
        )


def test_exact_marker_survives_dotenv(monkeypatch):
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "shell-marker")

    def fake_load(_path, *, override):
        assert override is False
        os.environ.setdefault("RESPAN_EXAMPLE_RUN_ID", "dotenv-marker")
        os.environ.setdefault("RESPAN_API_KEY", "test-key")

    monkeypatch.setattr(_shared, "load_dotenv", fake_load)
    _shared.load_root_env()
    assert _shared.marker() == "shell-marker"


def test_metadata_uses_exact_marker(monkeypatch):
    captured: dict[str, object] = {}

    class FakeRespan:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(_shared, "load_root_env", lambda: None)
    monkeypatch.setattr(_shared, "Respan", FakeRespan)
    monkeypatch.setenv("RESPAN_API_KEY", "test-key")
    _shared.make_respan("contract", "exact-marker")
    assert captured["metadata"]["example_run_id"] == "exact-marker"
    assert captured["metadata"]["run_id"] == "exact-marker"


def test_deterministic_clients_ignore_live_credentials(monkeypatch):
    monkeypatch.setattr(_shared, "load_root_env", lambda: None)
    monkeypatch.setenv("PORTKEY_API_KEY", "must-not-be-used")
    monkeypatch.setattr(_shared, "local_gateway_base_url", lambda: "http://127.0.0.1:9")
    assert _shared._client_kwargs(live=False) == {
        "api_key": "local-portkey-example-key",
        "base_url": "http://127.0.0.1:9",
    }


def test_runner_continues_and_aggregates(monkeypatch):
    calls: list[str] = []

    def fake_run(command, **kwargs):
        name = Path(command[-1]).name
        calls.append(name)
        assert kwargs["env"]["RESPAN_EXAMPLE_RUN_ID"] == "runner-marker"
        if name == "timeout.py":
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return SimpleNamespace(returncode=1 if name == "first.py" else 0)

    monkeypatch.setattr(run_all, "SCRIPTS", ("first.py", "timeout.py", "last.py"))
    monkeypatch.setattr(run_all.subprocess, "run", fake_run)
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "runner-marker")
    with pytest.raises(SystemExit) as caught:
        run_all.main()
    assert calls == ["first.py", "timeout.py", "last.py"]
    assert "first.py: exited 1" in str(caught.value)
    assert "timeout.py: timed out" in str(caught.value)


def test_runner_has_complete_set():
    assert len(run_all.SCRIPTS) == 6
    for script in run_all.SCRIPTS:
        assert (EXAMPLE_DIR / script).is_file()
