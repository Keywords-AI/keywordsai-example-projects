from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

import _shared
import pytest
import run_all_examples

EXAMPLE_DIR = Path(__file__).resolve().parent
SCRIPTS = (
    "01_sync_async.py",
    "02_streaming.py",
    "03_tool_calling.py",
    "04_expected_error.py",
    "05_privacy.py",
)


def test_runner_uses_exact_marker_timeout_and_every_example() -> None:
    runner = (EXAMPLE_DIR / "run_all_examples.py").read_text(encoding="utf-8")
    assert "require_run_id()" in runner
    assert 'environment["RESPAN_EXAMPLE_RUN_ID"] = run_id' in runner
    assert "timeout=EXAMPLE_TIMEOUT_SECONDS" in runner
    for script in SCRIPTS:
        assert script in runner


def test_runner_continues_and_aggregates_exit_and_timeout(monkeypatch) -> None:
    calls: list[str] = []

    def fake_run(command, **kwargs):
        script = Path(command[1]).name
        calls.append(script)
        assert kwargs["check"] is False
        assert kwargs["timeout"] == run_all_examples.EXAMPLE_TIMEOUT_SECONDS
        if script == SCRIPTS[0]:
            return subprocess.CompletedProcess(command, 7)
        if script == SCRIPTS[1]:
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(run_all_examples.subprocess, "run", fake_run)
    failures = run_all_examples.run_examples(
        "openlit-exact-marker",
        base_dir=EXAMPLE_DIR,
        python="python-test",
    )
    assert calls == list(SCRIPTS)
    assert failures == [f"{SCRIPTS[0]}: exit 7", f"{SCRIPTS[1]}: timeout"]


def test_examples_close_clients_and_flush_shutdown() -> None:
    shared = (EXAMPLE_DIR / "_shared.py").read_text(encoding="utf-8")
    assert "respan.flush()" in shared
    assert "respan.shutdown()" in shared
    assert "direct_url.json" in shared
    for script in SCRIPTS:
        source = (EXAMPLE_DIR / script).read_text(encoding="utf-8")
        assert "client.close()" in source
        assert "finish_respan(respan)" in source


def test_tool_error_privacy_and_stream_contracts_are_explicit() -> None:
    tool_source = (EXAMPLE_DIR / "03_tool_calling.py").read_text(encoding="utf-8")
    error_source = (EXAMPLE_DIR / "04_expected_error.py").read_text(encoding="utf-8")
    privacy_source = (EXAMPLE_DIR / "05_privacy.py").read_text(encoding="utf-8")
    stream_source = (EXAMPLE_DIR / "02_streaming.py").read_text(encoding="utf-8")
    assert '@tool(name="get_weather")' in tool_source
    assert "tool_call_id" in tool_source
    assert "status_code != 429" in error_source
    assert "capture_content=False" in privacy_source
    assert "PRIVATE_SENTINEL" in privacy_source
    assert "early.close()" in stream_source
    assert "stream.close()" in stream_source
    assert "await response_stream.close()" in stream_source
    assert "response.output_text.delta" in stream_source


def test_shell_marker_precedes_env_file_and_metadata_uses_exact_value(
    monkeypatch,
    tmp_path,
) -> None:
    marker = "openlit-shell-marker"
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", marker)
    env_file = tmp_path / ".env"
    env_file.write_text("RESPAN_EXAMPLE_RUN_ID=wrong-file-marker\n", encoding="utf-8")
    _shared._load_env_file(env_file)
    assert _shared.require_run_id() == marker
    assert _shared.example_metadata("scenario") == {
        "example_set": "python/tracing/openlit",
        "scenario": "scenario",
        "run_id": marker,
        "example_run_id": marker,
    }


def test_env_loader_preserves_shell_precedence(monkeypatch, tmp_path) -> None:
    env_file = tmp_path / ".env"
    calls: list[tuple[Path, bool]] = []

    def fake_load_dotenv(path: Path, *, override: bool) -> bool:
        calls.append((path, override))
        return True

    monkeypatch.setattr(_shared, "load_dotenv", fake_load_dotenv)
    _shared._load_env_file(env_file)
    assert calls == [(env_file, False)]


def test_marker_is_required_and_must_be_exact(monkeypatch) -> None:
    monkeypatch.delenv("RESPAN_EXAMPLE_RUN_ID", raising=False)
    with pytest.raises(RuntimeError, match="exact audit marker"):
        _shared.require_run_id()
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", " marker ")
    with pytest.raises(RuntimeError, match="exact audit marker"):
        _shared.require_run_id()


def test_workflow_inputs_are_bounded_semantics_not_provider_config() -> None:
    forbidden = {
        "api_key",
        "base_url",
        "client",
        "config",
        "credential",
        "secret",
        "token",
        "url",
    }
    for script in SCRIPTS:
        tree = ast.parse((EXAMPLE_DIR / script).read_text(encoding="utf-8"))
        decorated = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "workflow"
                for decorator in node.decorator_list
            )
        ]
        assert len(decorated) == 1
        workflow_function = decorated[0]
        argument_names = {argument.arg for argument in workflow_function.args.args}
        assert argument_names
        assert argument_names.isdisjoint(forbidden)

        workflow_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == workflow_function.name
        ]
        assert len(workflow_calls) == 1
        call = workflow_calls[0]
        assert not call.args
        actual_values = {
            keyword.arg: ast.literal_eval(keyword.value) for keyword in call.keywords
        }
        assert set(actual_values) == argument_names
        assert all(
            isinstance(value, str) and value.strip() for value in actual_values.values()
        )
        serialized = json.dumps(actual_values, sort_keys=True)
        assert len(serialized.encode("utf-8")) <= 512
        lowered = serialized.lower()
        assert all(marker not in lowered for marker in forbidden)
        assert "openlit-private-sentinel" not in lowered


def test_client_construction_is_bounded_and_non_retrying(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_sync(**kwargs):
        calls.append(("sync", kwargs))
        return "sync-client"

    def fake_async(**kwargs):
        calls.append(("async", kwargs))
        return "async-client"

    monkeypatch.setattr(_shared, "OpenAI", fake_sync)
    monkeypatch.setattr(_shared, "AsyncOpenAI", fake_async)
    config = _shared.ProviderConfig(
        api_key="provider-test-value",
        base_url="http://127.0.0.1:43123/v1",
        model="test-model",
        embedding_model="test-embedding-model",
        live=False,
    )

    assert _shared.sync_client(config) == "sync-client"
    assert _shared.async_client(config) == "async-client"
    assert calls == [
        (
            "sync",
            {
                "api_key": config.api_key,
                "base_url": config.base_url,
                "max_retries": 0,
                "timeout": 8,
            },
        ),
        (
            "async",
            {
                "api_key": config.api_key,
                "base_url": config.base_url,
                "max_retries": 0,
                "timeout": 8,
            },
        ),
    ]


def test_flush_shutdown_and_mock_server_teardown_are_fail_safe(
    monkeypatch,
) -> None:
    calls: list[str] = []

    class FakeRespan:
        def flush(self) -> None:
            calls.append("flush")
            raise RuntimeError("flush failed")

        def shutdown(self) -> None:
            calls.append("shutdown")

    with pytest.raises(RuntimeError, match="flush failed"):
        _shared.finish_respan(FakeRespan())
    assert calls == ["flush", "shutdown"]

    class FakeServer:
        server_port = 43123

        def __init__(self) -> None:
            self.shutdown_called = False
            self.close_called = False

        def serve_forever(self) -> None:
            return None

        def shutdown(self) -> None:
            self.shutdown_called = True

        def server_close(self) -> None:
            self.close_called = True

    class FakeThread:
        def __init__(self) -> None:
            self.started = False
            self.joined = False

        def start(self) -> None:
            self.started = True

        def join(self, timeout: int) -> None:
            assert timeout == 5
            self.joined = True

        def is_alive(self) -> bool:
            return False

    server = FakeServer()
    thread = FakeThread()
    monkeypatch.delenv("RESPAN_OPENLIT_LIVE", raising=False)
    monkeypatch.setattr(_shared, "ThreadingHTTPServer", lambda *args: server)
    monkeypatch.setattr(_shared.threading, "Thread", lambda **kwargs: thread)
    with _shared.provider_config() as config:
        assert config.base_url == "http://127.0.0.1:43123/v1"
        assert thread.started
    assert server.shutdown_called
    assert server.close_called
    assert thread.joined
