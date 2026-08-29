from __future__ import annotations

import ast
import asyncio
import importlib.util
import json
import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import _shared
import pytest
import run_all
from _loopback import AsyncCursor
from pgvector import Vector

EXAMPLE_DIR = Path(__file__).resolve().parent
DETERMINISTIC_SCRIPTS = (
    "01_sync_similarity.py",
    "02_async_similarity.py",
    "03_bulk_server_cursor_failure.py",
)


def _decorator_name(decorator: ast.expr) -> str | None:
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    return decorator.id if isinstance(decorator, ast.Name) else None


def test_workflow_roots_accept_only_bounded_semantic_inputs():
    expected_args = {
        "01_sync_similarity.py": ["query_vector", "limit"],
        "02_async_similarity.py": ["query_vector", "limit"],
        "03_bulk_server_cursor_failure.py": ["scenario"],
        "04_live_postgres.py": ["query_vector", "limit"],
    }
    for filename, semantic_args in expected_args.items():
        module = ast.parse((EXAMPLE_DIR / filename).read_text())
        workflows = [
            node
            for node in ast.walk(module)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(_decorator_name(item) == "workflow" for item in node.decorator_list)
        ]
        assert len(workflows) == 1
        assert [argument.arg for argument in workflows[0].args.args] == semantic_args
        assert workflows[0].args.kwonlyargs == []
        assert not {"sdk", "dsn", "client", "connection"}.intersection(semantic_args)


def test_workflow_calls_pass_bounded_nonsecret_semantic_values():
    workflow_calls = {
        "01_sync_similarity.py": "run_sync_similarity",
        "02_async_similarity.py": "run_async_similarity",
        "03_bulk_server_cursor_failure.py": "run_bulk_server_cursor_failure",
        "04_live_postgres.py": "run_live_postgres",
    }
    for filename, function_name in workflow_calls.items():
        module = ast.parse((EXAMPLE_DIR / filename).read_text())
        calls = [
            node
            for node in ast.walk(module)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == function_name
        ]
        assert len(calls) == 1
        values = [ast.literal_eval(argument) for argument in calls[0].args]
        encoded = json.dumps(values, separators=(",", ":"))
        assert values
        assert len(encoded.encode("utf-8")) <= 512
        assert not any(
            secret in encoded.lower()
            for secret in ("postgresql://", "password", "secret", "token", "dsn")
        )


def test_shell_marker_survives_dotenv_loading(monkeypatch):
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "shell-marker")

    def fake_load_dotenv(_path, *, override):
        assert override is False
        os.environ.setdefault("RESPAN_EXAMPLE_RUN_ID", "dotenv-marker")
        os.environ.setdefault("RESPAN_API_KEY", "test-key")

    monkeypatch.setattr(_shared, "load_dotenv", fake_load_dotenv)

    _shared.load_example_env()

    assert os.environ["RESPAN_EXAMPLE_RUN_ID"] == "shell-marker"


def test_default_respan_metadata_contains_exact_marker(monkeypatch):
    captured: dict[str, object] = {}

    class FakeRespan:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(_shared, "load_example_env", lambda: None)
    monkeypatch.setattr(_shared, "Respan", FakeRespan)
    monkeypatch.setenv("RESPAN_API_KEY", "test-key")

    _shared.create_respan("pgvector_contract_workflow", "exact-marker")

    assert captured["metadata"] == {
        "example_run_id": "exact-marker",
        "run_id": "exact-marker",
        "example_set": "pgvector",
        "workflow_name": "pgvector_contract_workflow",
    }
    assert captured["is_batching_enabled"] is False
    assert (
        _shared.workflow_attributes("pgvector_contract_workflow", "exact-marker")[
            "metadata"
        ]
        == captured["metadata"]
    )


def test_live_dsn_from_dotenv_is_loaded_before_the_skip_gate(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "pgvector_live_contract", EXAMPLE_DIR / "04_live_postgres.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calls: list[str] = []

    def load_repo_env() -> None:
        calls.append("load_env")
        os.environ.setdefault("PGVECTOR_DSN", "postgresql://dotenv-only/pgvector")

    async def fake_workflow(query_vector, limit):
        calls.append("workflow")
        assert query_vector == [0.1, 0.2, 0.3]
        assert limit == 1
        return {"ok": True}

    class FakeRespan:
        @staticmethod
        @contextmanager
        def propagate_attributes(**_kwargs):
            yield

    monkeypatch.delenv("PGVECTOR_DSN", raising=False)
    monkeypatch.setattr(module, "load_repo_env", load_repo_env)
    monkeypatch.setattr(module, "run_live_postgres", fake_workflow)
    monkeypatch.setattr(module, "create_respan", lambda *_: object())
    monkeypatch.setattr(module, "finish_respan", lambda _respan: calls.append("finish"))
    monkeypatch.setattr(module, "print_result", lambda *_: None)
    monkeypatch.setattr(module, "Respan", FakeRespan)
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "live-contract-marker")

    asyncio.run(module.run())

    assert calls == ["load_env", "workflow", "finish"]
    assert module.LIVE_DSN == "postgresql://dotenv-only/pgvector"


def test_live_example_covers_real_sync_async_server_cursor_and_psycopg2():
    source = (EXAMPLE_DIR / "04_live_postgres.py").read_text()
    requirements = (EXAMPLE_DIR / "requirements.txt").read_text()

    for required in (
        "psycopg.connect(_dsn())",
        "psycopg.AsyncConnection.connect(_dsn())",
        "respan_pgvector_live_server_cursor",
        "respan_pgvector_live_async_server_cursor",
        "pgvector_psycopg.register_vector(connection)",
        "pgvector_psycopg.register_vector_async(connection)",
        "pgvector_psycopg2.register_vector(connection)",
        "await extension.close()",
        "await create_cursor.close()",
        "await insert_cursor.close()",
        "await server_cursor.close()",
    ):
        assert required in source
    assert "psycopg2-binary" in requirements


def test_live_results_are_bounded_json_native_without_repr_or_str():
    spec = importlib.util.spec_from_file_location(
        "pgvector_live_result_contract", EXAMPLE_DIR / "04_live_postgres.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    bounded = module._bounded_row(("emoji-" + "😀" * 1000, Vector(list(range(1000)))))
    encoded = json.dumps(bounded, allow_nan=False, separators=(",", ":"))
    assert len(bounded["label"].encode("utf-8")) <= module.MAX_RESULT_TEXT_BYTES
    assert len(bounded["embedding"]["values"]) == module.MAX_RESULT_VECTOR_VALUES
    assert bounded["embedding"]["truncated"] is True
    assert "Vector(" not in encoded

    calls = {"repr": 0, "str": 0}

    class Hostile:
        def __repr__(self):
            calls["repr"] += 1
            raise AssertionError("repr must not run")

        def __str__(self):
            calls["str"] += 1
            raise AssertionError("str must not run")

        def to_list(self):
            raise AssertionError("to_list must not run")

    hostile = module._bounded_row(("safe", Hostile()))
    json.dumps(hostile, allow_nan=False)
    assert calls == {"repr": 0, "str": 0}
    assert hostile["embedding"]["values"] == []

    shared_source = (EXAMPLE_DIR / "_shared.py").read_text()
    assert "default=str" not in shared_source
    assert "allow_nan=False" in shared_source


def test_async_loopback_cursor_close_matches_real_sdk_shape():
    cursor = AsyncCursor()
    assert cursor.closed is False
    asyncio.run(cursor.close())
    assert cursor.closed is True


def test_runner_continues_and_aggregates_exit_and_timeout_failures(monkeypatch):
    calls: list[str] = []
    scripts = ("first.py", "timeout.py", "success.py")

    def fake_run(command, **kwargs):
        script = Path(command[-1]).name
        calls.append(script)
        assert kwargs["check"] is False
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
    message = str(caught.value)
    assert "first.py: exited 1" in message
    assert "timeout.py: timed out" in message


def test_runner_contains_all_committed_scenarios():
    assert run_all.SCRIPTS == (*DETERMINISTIC_SCRIPTS, "04_live_postgres.py")
    for script in run_all.SCRIPTS:
        assert (EXAMPLE_DIR / script).is_file()
