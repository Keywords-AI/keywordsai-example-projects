from __future__ import annotations

from types import SimpleNamespace

import _shared
import pytest
import run_all


def test_repo_dotenv_does_not_override_exact_invocation_marker(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    (tmp_path / ".env").write_text(
        "RESPAN_EXAMPLE_RUN_ID=dotenv-marker\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(_shared, "PROJECT_ROOT", tmp_path)
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "shell-marker")

    assert _shared.example_run_id() == "shell-marker"


def test_compat_server_cleanup_joins_and_resets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    class FakeServer:
        def shutdown(self) -> None:
            calls.append("shutdown")

        def server_close(self) -> None:
            calls.append("server_close")

    class FakeThread:
        def join(self, timeout: int) -> None:
            calls.append(f"join:{timeout}")

    monkeypatch.setattr(_shared, "_FAKE_SERVER", FakeServer())
    monkeypatch.setattr(_shared, "_FAKE_SERVER_THREAD", FakeThread())

    _shared._stop_fake_ollama_server()

    assert calls == ["shutdown", "server_close", "join:2"]
    assert _shared._FAKE_SERVER is None
    assert _shared._FAKE_SERVER_THREAD is None


def test_run_all_preserves_marker_and_reports_every_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    return_codes = iter([0, 2, 0, 3, 0])
    calls: list[tuple[str, str]] = []

    def run(command, *, cwd, env, check):
        calls.append((command[-1], env["RESPAN_EXAMPLE_RUN_ID"]))
        assert cwd == run_all.EXAMPLE_DIR
        assert check is False
        return SimpleNamespace(returncode=next(return_codes))

    monkeypatch.setattr(run_all.subprocess, "run", run)
    monkeypatch.setenv("RESPAN_EXAMPLE_RUN_ID", "shell-marker")

    with pytest.raises(SystemExit, match="02_stream_generate.py.*04_embeddings.py"):
        run_all.main()

    assert len(calls) == 5
    assert {marker for _, marker in calls} == {"shell-marker"}
