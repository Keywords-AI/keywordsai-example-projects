from __future__ import annotations

import ast
import asyncio
import gc
import logging
import subprocess
import traceback
from pathlib import Path
from types import SimpleNamespace

import _shared
import pytest
import run_all
from respan_instrumentation_openai import _otel_emitter as openai_emitter
from respan_instrumentation_openrouter import OpenRouterInstrumentor


def test_requirements_match_the_validated_openai_surface() -> None:
    requirements = (Path(__file__).parent / "requirements.txt").read_text(
        encoding="utf-8"
    )

    assert "openai>=3.0.0,<4.0.0" in requirements.splitlines()
    assert "respan-instrumentation-openai>=1.2.1,<2.0.0" in requirements.splitlines()


def test_examples_do_not_prepend_unmerged_instrumentation_sources() -> None:
    here = Path(__file__).resolve().parent
    shared = (here / "_shared.py").read_text(encoding="utf-8")
    readme = (here / "README.md").read_text(encoding="utf-8")

    assert "sys.path" not in shared
    assert "respan-instrumentation-openai" not in shared
    assert (
        "$RESPAN_REPO/python-sdks/instrumentations/respan-instrumentation-openai"
        not in readme
    )


def test_env_file_does_not_override_shell_marker(monkeypatch, tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "RESPAN_EXAMPLE_RUN_ID=stale-file-marker\nOPENROUTER_MODEL=file-model\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "shell-marker")
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)

    _shared._load_env_file(env_file)

    assert _shared.os.environ["RESPAN_EXAMPLE_RUN_ID"] == "shell-marker"
    assert _shared.os.environ["OPENROUTER_MODEL"] == "file-model"


def test_make_respan_emits_both_exact_marker_metadata_keys(monkeypatch) -> None:
    captured = {}

    def fake_respan(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace()

    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "marker-123")
    monkeypatch.setattr(_shared, "ensure_respan_api_key", lambda: "respan-test-key")
    monkeypatch.setattr(_shared, "Respan", fake_respan)

    _shared.make_respan(scenario="contract")

    assert captured["metadata"]["run_id"] == "marker-123"
    assert captured["metadata"]["example_run_id"] == "marker-123"
    assert captured["metadata"]["scenario"] == "contract"


def test_live_key_does_not_switch_deterministic_examples(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "live-key-must-not-be-used")
    monkeypatch.setattr(
        _shared,
        "_mock_base_url",
        lambda: "http://127.0.0.1:43123/api/v1",
    )

    deterministic = _shared.openrouter_config()
    live = _shared.openrouter_config(live=True)

    assert deterministic == {
        "api_key": "openrouter-mock-key",
        "base_url": "http://127.0.0.1:43123/api/v1",
        "model": _shared.os.getenv(
            "OPENROUTER_MODEL",
            _shared.DEFAULT_OPENROUTER_MODEL,
        ),
    }
    assert live["api_key"] == "live-key-must-not-be-used"
    assert live["base_url"] == _shared.os.getenv(
        "OPENROUTER_BASE_URL",
        _shared.DEFAULT_OPENROUTER_BASE_URL,
    )


def test_runner_aggregates_exit_failures_and_timeouts(monkeypatch) -> None:
    monkeypatch.setattr(run_all, "EXAMPLES", ["fail.py", "slow.py", "pass.py"])
    monkeypatch.delenv("RESPAN_EXAMPLE_RUN_ID", raising=False)
    calls = []

    def fake_run(command, *, check, env, timeout):
        calls.append((command, check, env, timeout))
        if command[-1].endswith("fail.py"):
            return subprocess.CompletedProcess(command, 7)
        if command[-1].endswith("slow.py"):
            raise subprocess.TimeoutExpired(command, timeout)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(run_all.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError) as exc_info:
        run_all.run()

    assert len(calls) == 3
    markers = {call[2]["RESPAN_EXAMPLE_RUN_ID"] for call in calls}
    assert len(markers) == 1
    assert next(iter(markers)).startswith("otel2-openrouter-local-")
    assert "fail.py: exit 7" in str(exc_info.value)
    assert "slow.py: timeout" in str(exc_info.value)


def test_sync_teardown_continues_after_close_and_flush_failures(monkeypatch) -> None:
    calls = []

    class Client:
        def close(self) -> None:
            calls.append("close")
            raise RuntimeError("close failed")

    class Respan:
        def flush(self) -> None:
            calls.append("flush")
            raise RuntimeError("flush failed")

        def shutdown(self) -> None:
            calls.append("shutdown")

    monkeypatch.setattr(
        _shared,
        "_shutdown_mock_server",
        lambda: calls.append("mock_shutdown"),
    )

    with pytest.raises(RuntimeError, match="close failed"):
        _shared.close_sync(respan=Respan(), client=Client())

    assert calls == ["close", "flush", "shutdown", "mock_shutdown"]


def test_async_teardown_continues_after_close_failure(monkeypatch) -> None:
    calls = []

    class Client:
        async def close(self) -> None:
            calls.append("close")
            raise RuntimeError("async close failed")

    class Respan:
        def flush(self) -> None:
            calls.append("flush")

        def shutdown(self) -> None:
            calls.append("shutdown")

    monkeypatch.setattr(
        _shared,
        "_shutdown_mock_server",
        lambda: calls.append("mock_shutdown"),
    )

    async def run() -> None:
        with pytest.raises(RuntimeError, match="async close failed"):
            await _shared.close_async(respan=Respan(), client=Client())

    asyncio.run(run())
    assert calls == ["close", "flush", "shutdown", "mock_shutdown"]


def test_tool_example_uses_tool_boundary_and_requirements_are_portable() -> None:
    here = Path(__file__).resolve().parent
    tool_example = (here / "03_tool_calling.py").read_text(encoding="utf-8")
    requirements = (here / "requirements.txt").read_text(encoding="utf-8")

    assert '@tool(name="get_weather")' in tool_example
    assert "@task" not in tool_example
    assert "-e " not in requirements


def test_only_explicit_live_example_enables_live_provider() -> None:
    here = Path(__file__).resolve().parent

    for filename in run_all.EXAMPLES:
        source = (here / filename).read_text(encoding="utf-8")
        if filename == "08_live_provider.py":
            assert "make_client(live=True)" in source
        else:
            assert "live=True" not in source


def test_stream_examples_exercise_transport_context_managers() -> None:
    here = Path(__file__).resolve().parent
    sync_stream = (here / "02_streaming_chat.py").read_text(encoding="utf-8")
    async_stream = (here / "06_async_streaming_chat.py").read_text(encoding="utf-8")

    assert "with stream:" in sync_stream
    assert "async with stream:" in async_stream


@pytest.mark.parametrize("instrumented", [False, True], ids=["bare-openai", "proxy"])
def test_async_stream_transport_teardown_has_no_asyncgen_warning(
    caplog,
    monkeypatch,
    instrumented: bool,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_USE_RESPAN_GATEWAY", raising=False)
    monkeypatch.setattr(openai_emitter, "inject_span", lambda span: True)
    instrumentor = OpenRouterInstrumentor()

    async def exercise_transport() -> list[str]:
        client, model = _shared.make_async_client()
        if instrumented:
            instrumentor.activate()

        async def consume(index: int) -> str:
            stream = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": f"transport run {index}"}],
                stream=True,
                stream_options={"include_usage": True},
            )
            parts = []
            async with stream:
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        parts.append(chunk.choices[0].delta.content)
            return "".join(parts)

        try:
            return await asyncio.gather(*(consume(index) for index in range(8)))
        finally:
            await client.close()
            if instrumented:
                instrumentor.deactivate()
            _shared._shutdown_mock_server()

    caplog.set_level(logging.ERROR, logger="asyncio")
    outputs = asyncio.run(exercise_transport())
    gc.collect()

    assert outputs == ["Trace data flows clearly."] * 8
    logged = []
    for record in caplog.records:
        message = record.getMessage()
        if record.exc_info:
            message += "\n" + "".join(traceback.format_exception(*record.exc_info))
        logged.append(message)
    combined = "\n".join(logged)
    assert "closing of asynchronous generator" not in combined
    assert "generator didn't stop after athrow()" not in combined


def test_async_stream_supports_done_protocol(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_USE_RESPAN_GATEWAY", raising=False)
    monkeypatch.setattr(openai_emitter, "inject_span", lambda span: True)
    instrumentor = OpenRouterInstrumentor()

    async def exercise_transport() -> str:
        client, model = _shared.make_async_client()
        instrumentor.activate()
        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "DONE protocol compatibility"}],
                stream=True,
                stream_options={"include_usage": True},
                extra_headers={"x-respan-mock-stream-termination": "done"},
            )
            parts = []
            async with stream:
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        parts.append(chunk.choices[0].delta.content)
            return "".join(parts)
        finally:
            await client.close()
            instrumentor.deactivate()
            _shared._shutdown_mock_server()

    assert asyncio.run(exercise_transport()) == "Trace data flows clearly."


def test_each_workflow_has_one_bounded_semantic_root_argument() -> None:
    here = Path(__file__).resolve().parent
    expected_arguments = {
        "01_chat_completion.py": "prompt",
        "02_streaming_chat.py": "prompt",
        "03_tool_calling.py": "question",
        "04_async_chat.py": "prompt",
        "05_structured_output.py": "topic",
        "06_async_streaming_chat.py": "prompt",
        "07_expected_error.py": "trigger_prompt",
        "08_live_provider.py": "prompt",
    }

    for filename, expected_argument in expected_arguments.items():
        tree = ast.parse((here / filename).read_text(encoding="utf-8"))
        run_functions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "run"
        ]
        assert len(run_functions) == 1, filename
        argument_names = [argument.arg for argument in run_functions[0].args.args]
        assert argument_names == [expected_argument], filename
        assert "client" not in argument_names
        assert "model" not in argument_names
