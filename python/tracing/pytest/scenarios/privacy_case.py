from __future__ import annotations


def test_capture_disabled_failure() -> None:
    raise RuntimeError("api_key=pytest-secret-must-not-export")
