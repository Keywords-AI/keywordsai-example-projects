"""Focused contract checks for the bounded all-example runner."""

from __future__ import annotations

import subprocess

import run_all


def test_timeout_is_reported_without_stopping_later_commands(monkeypatch, capsys):
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        if len(calls) == 1:
            raise subprocess.TimeoutExpired(command, timeout=7)
        return subprocess.CompletedProcess(command, returncode=0)

    monkeypatch.setattr(run_all.subprocess, "run", fake_run)
    commands = [["python", "slow.py"], ["python", "next.py"]]

    failures = run_all._run_commands(commands, env={}, timeout_seconds=7)

    assert calls == commands
    assert failures == [(commands[0], "timeout after 7s")]
    assert "[2/2] python next.py" in capsys.readouterr().out
