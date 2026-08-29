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


def _workflow_signatures(filename: str) -> list[list[str]]:
    module = ast.parse((EXAMPLE_DIR / filename).read_text())
    workflows = [
        node
        for node in ast.walk(module)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Name)
            and decorator.func.id == "workflow"
            for decorator in node.decorator_list
        )
    ]
    return [[argument.arg for argument in node.args.args] for node in workflows]


def test_roots_capture_only_bounded_semantic_inputs():
    assert _workflow_signatures("01_offline_pipeline.py") == [["prompt"]]
    assert _workflow_signatures("02_gateway_llm_pipeline.py") == [["prompt"]]
    assert _workflow_signatures("03_expected_error.py") == [["prompt"]]


def test_current_worker_api_replaces_deprecated_task_and_runner():
    for filename in run_all.SCRIPTS:
        source = (EXAMPLE_DIR / filename).read_text()
        assert "PipelineTask" not in source
        assert "PipelineRunner" not in source
    shared_source = (EXAMPLE_DIR / "_pipeline.py").read_text()
    assert "PipelineWorker" in shared_source
    assert "WorkerRunner" in shared_source
    assert "add_workers" in shared_source


def test_shell_marker_survives_dotenv(monkeypatch):
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "exact-shell-marker")

    def fake_load_dotenv(_path, *, override):
        assert override is False
        os.environ.setdefault("RESPAN_EXAMPLE_RUN_ID", "dotenv-marker")
        os.environ.setdefault("RESPAN_API_KEY", "test-key")

    monkeypatch.setattr(_shared, "load_dotenv", fake_load_dotenv)
    _shared.load_example_env()
    assert _shared.marker() == "exact-shell-marker"


def test_respan_and_workflow_metadata_use_exact_marker(monkeypatch):
    captured: dict[str, object] = {}

    class FakeRespan:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(_shared, "load_example_env", lambda: None)
    monkeypatch.setattr(_shared, "Respan", FakeRespan)
    monkeypatch.setenv("RESPAN_API_KEY", "test-key")
    _shared.create_respan("pipecat_contract", "exact-marker")

    assert captured["metadata"] == {
        "example_set": "pipecat",
        "workflow_name": "pipecat_contract",
        "example_run_id": "exact-marker",
        "run_id": "exact-marker",
    }
    attrs = _shared.workflow_attributes(
        "pipecat_contract", "exact-marker", "execution-1", mode="deterministic"
    )
    assert attrs["metadata"]["example_run_id"] == "exact-marker"
    assert attrs["metadata"]["run_id"] == "exact-marker"


def test_runner_continues_and_aggregates_failures(monkeypatch):
    scripts = ("first.py", "timeout.py", "last.py")
    calls: list[str] = []

    def fake_run(command, **kwargs):
        script = Path(command[-1]).name
        calls.append(script)
        assert kwargs["env"]["RESPAN_EXAMPLE_RUN_ID"] == "runner-marker"
        if script == "timeout.py":
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return SimpleNamespace(returncode=1 if script == "first.py" else 0)

    monkeypatch.setattr(run_all, "SCRIPTS", scripts)
    monkeypatch.setattr(run_all.subprocess, "run", fake_run)
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "runner-marker")
    with pytest.raises(SystemExit) as caught:
        run_all.main()
    assert calls == list(scripts)
    assert "first.py: exited 1" in str(caught.value)
    assert "timeout.py: timed out" in str(caught.value)


def test_runner_contains_complete_committed_set():
    assert run_all.SCRIPTS == (
        "01_offline_pipeline.py",
        "02_gateway_llm_pipeline.py",
        "03_expected_error.py",
    )
    for script in run_all.SCRIPTS:
        assert (EXAMPLE_DIR / script).is_file()
